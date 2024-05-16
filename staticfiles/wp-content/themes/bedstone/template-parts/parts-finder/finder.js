function capitalize(str) {
	return str.charAt(0).toUpperCase() + str.slice(1);
}

Object.filter = (obj, predicate) =>
	Object.keys(obj)
		.filter((key) => predicate(obj[key]))
		.reduce((res, key) => ((res[key] = obj[key]), res), {});

window.addEventListener('DOMContentLoaded', () => {
	document.querySelectorAll('.partsFinderMenuToggle')?.forEach((toggle) => {
		toggle.addEventListener('click', (ev) => {
			console.log(ev);
			ev.preventDefault();

			document.body.classList.remove('nav-main--active');
			document.body.classList.remove('mobile-menu--active');
			document
				.querySelector('.toggle-nav-main__wrap')
				?.setAttribute('aria-expanded', 'false');

			document
				.getElementById('partsFinderHeaderSearchBoxContainer')
				?.classList.toggle('hidden');
		});
	});
});

document.addEventListener('alpine:init', () => {
	Alpine.data('partsFinder', () => ({
		totalPages: 0,
		currentPage: 0,
		partsResults: null,
		isFetching: false,
		activeFilters: {},
		searchParams: new URLSearchParams(window.location.search),
		vehicle: null,
		categories: null,
		vehicleString: null,

		async init() {
			console.log('initializing finder');
			let payload = {};
			let categories = this.searchParams.has('categories')
				? this.searchParams.get('categories').split(',')
				: [];
			let subcategories = this.searchParams.has('subcategories')
				? this.searchParams.get('subcategories').split(',')
				: [];

			if (categories.length > 0) {
				payload.categories = categories;
			}

			if (subcategories.length > 0) {
				payload.subcategories = subcategories;

				subcategories.forEach((subcategory) => {
					const categoryTarget = Object.filter(window.processedCategories, (c) => {
						// console.log(
						// 	c.subcategories,
						// 	subcategory,
						// 	c.subcategories.includes(subcategory)
						// );
						return (
							c.subcategories.filter((subc) => subc.value === subcategory).length > 0
						);
					});

					if (categoryTarget) {
						const category = Object.values(categoryTarget)[0].value;

						if (
							category in this.activeFilters &&
							this.activeFilters[category].includes(subcategory)
						) {
							this.activeFilters[category].splice(
								this.activeFilters[category].indexOf(subcategory),
								1
							);

							if (this.activeFilters[category].length === 0)
								delete this.activeFilters[category];

							return;
						}

						this.activeFilters[category] =
							category in this.activeFilters
								? [...new Set([...this.activeFilters[category], subcategory])]
								: [subcategory];
					}

					console.log(categoryTarget);
				});
			}

			if (typeof window.partFinderCategory !== 'undefined') {
				payload.categories = window.partFinderCategory;
				this.activeFilters[window.partFinderCategory] = subcategories;
			}

			if (this.searchParams.has('partNumbers')) {
				payload.partNumbers = this.searchParams.get('partNumbers').split(',');
			}

			if (this.searchParams.has('interchange')) {
				payload.interchange = this.searchParams.get('interchange');
			}

			if (this.searchParams.has('vin')) {
				await this.decodeVin(this.searchParams.get('vin'));

				if (this.vehicle) {
					const setVehicleEvent = new CustomEvent('set-vehicle', {
						detail: { vehicle: this.vehicle },
					});

					window.dispatchEvent(setVehicleEvent);
				}

				payload = { ...payload, ...this.vehicle };
			}

			if (
				this.searchParams.has('y') &&
				this.searchParams.has('make') &&
				this.searchParams.has('model') &&
				this.searchParams.has('engine')
			) {
				this.vehicle = {};
				this.vehicle.year = this.searchParams.get('y');
				this.vehicle.make = this.searchParams.get('make');
				this.vehicle.model = this.searchParams.get('model');
				this.vehicle.engine = this.searchParams.get('engine');
				this.vehicleString = `Results for: ${this.vehicle.year} ${capitalize(
					this.vehicle.make
				)}  ${capitalize(this.vehicle.model)} ${this.vehicle.engine}L`;

				payload = { ...payload, ...this.vehicle };
			}

			if (this.searchParams.has('category')) {
				this.activeFilters[this.searchParams.get('category')] = subcategories;

				payload = { ...payload, category: this.searchParams.get('category') };
			}

			const r = await this.postCall('get_paginated_parts', payload);

			console.log(r, payload);

			this.partsResults = r.parts;
			this.totalPages = Object.keys(payload).length === 0 ? 0 : Math.ceil(r.total / 9);
			this.currentPage = r.page;

			window.addEventListener('fetching', (ev) => {
				this.isFetching = ev.detail.isFetching;
			});
		},

		async decodeVin(VIN) {
			if (!VIN) return;

			const data = await this.postCall('decode_vin', {
				VIN: VIN,
			});

			this.vehicle = {};
			this.vehicle.year = data?.Results[0]?.ModelYear;
			this.vehicle.make = data?.Results[0]?.Make;
			this.vehicle.model = data?.Results[0]?.Model;
			this.vehicle.engine =
				data?.Results[0]?.DisplacementL.length === 1
					? `${data?.Results[0]?.DisplacementL}.0`
					: data?.Results[0]?.DisplacementL;
		},

		async clearFilterClickHandler(ev) {
			this.activeFilters = {};
			await this.getPaginatedParts();

			window.history.pushState({}, '', window.location.pathname);
		},

		async pageClickHandler(page) {
			if (this.currentPage === page) return;

			this.currentPage = page;

			await this.getPaginatedParts(page);

			window.scroll({
				top: document.getElementById('mtr-parts-finder-container')?.offsetTop ?? 0,
				behavior: 'smooth',
			});
		},

		async categoryClickHandler(ev) {
			const category = ev.target.dataset.category;
			const subcategory = ev.target.dataset.subcategory;

			if (
				category in this.activeFilters &&
				this.activeFilters[category].includes(subcategory)
			) {
				this.activeFilters[category].splice(
					this.activeFilters[category].indexOf(subcategory),
					1
				);

				if (this.activeFilters[category].length === 0) delete this.activeFilters[category];

				await this.getPaginatedParts();

				return;
			}

			this.activeFilters[category] =
				category in this.activeFilters
					? [...new Set([...this.activeFilters[category], subcategory])]
					: [subcategory];

			await this.getPaginatedParts();
		},

		async getPaginatedParts(page) {
			let payload = {};
			const categories = Object.keys(this.activeFilters);
			const subcategories = Object.values(this.activeFilters).flat();

			if (categories.length > 0) payload.categories = categories;
			if (subcategories.length > 0) payload.subcategories = subcategories;
			payload.page = page ? page : this.currentPage;

			if (this.searchParams.has('partNumbers')) {
				payload.partNumbers = this.searchParams.get('partNumbers').split(',');
			}

			if (this.vehicle !== null) payload = { ...payload, ...this.vehicle };

			if (this.searchParams.has('category'))
				payload = { ...payload, category: this.searchParams.get('category') };

			let paramsPayload = this.searchParams;

			if (this.vehicle) {
				paramsPayload = {
					...paramsPayload,
					make: this.vehicle.make,
					model: this.vehicle.model,
					engine: this.vehicle.engine,
					y: this.vehicle.year,
				};
			}

			paramsPayload = {
				...paramsPayload,
				categories: Object.keys(this.activeFilters),
				subcategories: Object.values(this.activeFilters).flat(),
			};

			window.history.pushState(
				{},
				'',
				`${window.location.pathname}?${new URLSearchParams(paramsPayload).toString()}`
			);

			const r = await this.postCall('get_paginated_parts', payload);

			this.partsResults = r.parts;
			this.totalPages = Math.ceil(r.total / 9);
			this.currentPage = r.page;
		},

		async postCall(action, data) {
			const formData = new FormData();

			formData.append('action', action);

			for (const [key, value] of Object.entries(data)) {
				formData.append(key, value);
			}

			this.isFetching = true;

			const response = await fetch('/wp-admin/admin-ajax.php', {
				method: 'POST',
				body: formData,
			});

			this.isFetching = false;

			return await response.json();
		},
	}));

	Alpine.data('searchBox', () => ({
		windowSearchParams: new URLSearchParams(window.location.search),
		searchType: 'vehicle',
		years: [...Array(new Date().getFullYear() + 1).keys()]
			.filter((y) => y > 1919)
			.sort((yearA, yearB) => yearB - yearA),
		makes: [],
		models: [],
		engines: [],
		categories: [],
		vehicle: null,
		partNumbers: null,
		partNumber: '',
		VIN: '',
		interchange: '',
		licensePlate: '',
		licensePlateState: '',
		searchClicked: false,
		selections: {
			year: '',
			make: '',
			model: '',
			engine: '',
			category: '',
		},
		totalPages: 0,

		async init() {
			console.log('initializing searchbox');

			const categories = await this.postCall('get_major_categories');

			this.categories = categories;

			if (this.windowSearchParams.get('category')) {
				this.selections.category = this.windowSearchParams.get('category');
			}

			if (this.windowSearchParams.get('y')) {
				this.selections.year = this.windowSearchParams.get('y');
				await this.getMakes();
			}

			if (this.windowSearchParams.get('make')) {
				this.selections.make = this.windowSearchParams.get('make');
				await this.getModels();
			}

			if (this.windowSearchParams.get('model')) {
				this.selections.model = this.windowSearchParams.get('model');
				await this.getEngines();
			}

			if (this.windowSearchParams.get('engine')) {
				this.selections.engine = this.windowSearchParams.get('engine');
				this.searchClicked = true;

				await this.getVehicle();
			}

			if (this.windowSearchParams.get('plate')) {
				this.searchType = 'license_plate';
				this.licensePlate = this.windowSearchParams.get('plate');
				this.licensePlateState = this.windowSearchParams.get('state');
				await this.decodePlate();
			}

			if (this.windowSearchParams.get('vin')) {
				this.searchType = 'vin';
				this.VIN = this.windowSearchParams.get('vin');
				// await this.decodeVin();
			}

			if (this.windowSearchParams.get('interchange')) {
				this.searchType = 'interchange';
				this.interchange = this.windowSearchParams.get('interchange');
				// await this.getInterchangeParts();
			}

			this.$watch('searchType', (value) => {
				if (value !== 'vehicle') {
					this.vehicle = null;
					this.selections = {
						year: '',
						make: '',
						model: '',
						engine: '',
						category: '',
					};
					this.makes = [];
					this.models = [];
					this.engines = [];
				}

				if (value !== 'vin') this.VIN = '';
			});

			window.addEventListener('set-vehicle', (ev) => {
				this.vehicle = {
					...ev.detail.vehicle,
					displacement_liters: ev.detail.vehicle.engine,
				};

				this.selections = {
					year: this.vehicle.year,
					make: this.vehicle.make,
					model: this.vehicle.model,
					engine: this.vehicle.engine,
					category: '',
				};
			});
		},

		async findHandler() {
			switch (this.searchType) {
				case 'vehicle':
					const selectionsClone = Object.entries(this.selections).reduce(
						(acc, [k, v]) => (v ? { ...acc, [k]: v } : acc),
						{}
					);

					selectionsClone.y = selectionsClone.year;

					delete selectionsClone.year;

					const searchString = new URLSearchParams(selectionsClone).toString();

					window.location = `${
						window.currentLanguageCode ? '/' + window.currentLanguageCode + '/' : '/'
					}products/?${searchString}`;
					return;

				case 'part_number':
					window.location = `${
						window.currentLanguageCode ? '/' + window.currentLanguageCode + '/' : '/'
					}products/?partNumbers=${this.partNumber}`;
					return;

				case 'vin':
					window.location = `${
						window.currentLanguageCode ? '/' + window.currentLanguageCode + '/' : '/'
					}products/?vin=${this.VIN}`;
					return;

				case 'license_plate':
					window.location = `${
						window.currentLanguageCode ? '/' + window.currentLanguageCode + '/' : '/'
					}products/?plate=${this.licensePlate}&state=${this.licensePlateState}`;
					return;

				case 'interchange':
					window.location = `${
						window.currentLanguageCode ? '/' + window.currentLanguageCode + '/' : '/'
					}products/?interchange=${this.interchange}`;
					return;

				default:
					console.log('Nothing to do.');
					break;
			}

			const payload = { partNumbers: this.partsResults.map((p) => p.part_number) };

			window.location =
				this.partsResults.length === 0
					? '/products/?no-results'
					: '/products/?' + new URLSearchParams(payload).toString();
		},

		searchHandler(ev) {
			ev.preventDefault();

			this.searchClicked = true;

			window.history.pushState({}, '', window.location.pathname);

			switch (this.searchType) {
				case 'vehicle':
					const selectionsClone = Object.entries(this.selections).reduce(
						(acc, [k, v]) => (v ? { ...acc, [k]: v } : acc),
						{}
					);

					selectionsClone.y = selectionsClone.year;

					delete selectionsClone.year;

					const searchString = new URLSearchParams(selectionsClone).toString();

					window.history.pushState({}, '', `/products/?${searchString}`);

					this.getParts();
					break;

				case 'part_number':
					this.getPart();
					break;

				case 'vin':
					this.decodeVin();
					break;

				case 'license_plate':
					this.decodePlate();
					break;

				case 'interchange':
					this.getInterchangeParts();
					break;

				default:
					console.log('Nothing to do.');
					break;
			}
		},

		async postCall(action, data = {}) {
			const formData = new FormData();

			formData.append('action', action);

			for (const [key, value] of Object.entries(data)) {
				formData.append(key, value);
			}

			const fetchEvent = new CustomEvent('fetching', {
				detail: { isFetching: true },
			});

			const fetchEventFalse = new CustomEvent('fetching', {
				detail: { isFetching: false },
			});

			window.dispatchEvent(fetchEvent);

			const response = await fetch('/wp-admin/admin-ajax.php', {
				method: 'POST',
				body: formData,
			});

			const result = await response.json();

			if (result.length === 0) {
				this.totalPages = 0;
			}

			window.dispatchEvent(fetchEventFalse);

			return result;
		},

		async decodeVin() {
			if (this.VIN === '') return;

			const data = await this.postCall('decode_vin', {
				VIN: this.VIN,
			});

			if (data?.Results[0]?.ErrorCode !== '0') {
				this.partNumbers = null;
				this.partsResults = [];
				return;
			}

			this.selections.year = data?.Results[0]?.ModelYear;
			this.selections.make = data?.Results[0]?.Make;
			this.selections.model = data?.Results[0]?.Model;
			this.selections.engine = data?.Results[0]?.DisplacementL;

			await this.getVehicle();

			await this.getParts();
		},

		async decodePlate() {
			if (this.licensePlate === '' || this.licensePlateState === '') return;

			const data = await this.postCall('get_license_plate', {
				plate: this.licensePlate,
				state: this.licensePlateState,
			});

			if (data?.vin) {
				this.VIN = data.vin;

				await this.decodeVin();
			} else {
				this.partsResults = [];
			}
		},

		async getMakes() {
			this.searchClicked = false;
			this.selections.make = '';
			this.selections.model = '';
			this.selections.engine = '';
			this.models = [];
			this.engines = [];
			this.vehicle = null;

			if (this.selections.year === '') {
				this.makes = [];
				return;
			}

			this.makes = await this.postCall('get_makes', {
				year: this.selections.year,
			});
		},

		async getModels() {
			this.searchClicked = false;
			this.selections.model = '';
			this.selections.engine = '';
			this.engines = [];
			this.vehicle = null;

			if (this.selections.year === '' || this.selections.make === '') {
				this.models = [];
				return;
			}

			this.models = await this.postCall('get_models', {
				year: this.selections.year,
				make: this.selections.make,
			});
		},

		async getEngines() {
			this.searchClicked = false;
			this.selections.engine = '';
			this.vehicle = null;

			if (
				this.selections.year === '' ||
				this.selections.make === '' ||
				this.selections.model === ''
			) {
				this.engines = [];
				return;
			}

			this.engines = await this.postCall('get_engines', {
				year: this.selections.year,
				make: this.selections.make,
				model: this.selections.model,
			});
		},

		async getVehicle() {
			if (
				this.selections.year === '' ||
				this.selections.make === '' ||
				this.selections.model === '' ||
				this.selections.engine === ''
			) {
				this.vehicle = null;
				return;
			}

			let payload = {
				year: this.selections.year,
				make: this.selections.make,
				model: this.selections.model,
				engine: this.selections.engine,
			};

			const data = await this.postCall('get_vehicle', payload);

			if (data.length === 0) {
				this.partsResults = [];

				return;
			}

			if (data !== '' && typeof data[0] !== 'undefined') {
				this.vehicle = data[0];
				this.partNumbers = [
					...data[0]?.coverage_parts.split(','),
					...data[0]?.choice_parts.split(','),
				].filter((p) => p);
			}
		},

		async getParts() {
			if (this.partNumbers === null) {
				return;
			}

			let payload = { part_numbers: this.partNumbers };

			if (this.selections.category !== '') payload.category = this.selections.category;

			this.partsResults = await this.postCall('get_parts', payload);
		},

		async getPart() {
			if (this.partNumber === '') {
				return;
			}

			this.partsResults = await this.postCall('get_part', {
				part_number: this.partNumber,
			});
		},

		async getInterchangeParts() {
			if (this.interchange === '') {
				return;
			}

			this.partsResults = await this.postCall('get_interchange_parts', {
				part_number: this.interchange,
			});
		},
	}));

	Alpine.data('searchBoxShortcode', () => ({
		windowSearchParams: new URLSearchParams(window.location.search),
		searchType: 'vehicle',
		years: [...Array(new Date().getFullYear() + 1).keys()]
			.filter((y) => y > 1919)
			.sort((yearA, yearB) => yearB - yearA),
		makes: [],
		models: [],
		engines: [],
		categories: [],
		vehicle: null,
		partNumbers: null,
		partNumber: '',
		VIN: '',
		interchange: '',
		licensePlate: '',
		licensePlateState: '',
		searchClicked: false,
		selections: {
			year: '',
			make: '',
			model: '',
			engine: '',
			category: '',
		},

		async init() {
			console.log('initializing searchbox shortcode');

			const categories = await this.postCall('get_major_categories');

			this.categories = categories;

			if (this.windowSearchParams.get('y')) {
				this.selections.year = this.windowSearchParams.get('y');
				await this.getMakes();
			}

			if (this.windowSearchParams.get('make')) {
				this.selections.make = this.windowSearchParams.get('make');
				await this.getModels();
			}

			if (this.windowSearchParams.get('model')) {
				this.selections.model = this.windowSearchParams.get('model');
				await this.getEngines();
			}

			if (this.windowSearchParams.get('engine')) {
				this.selections.engine = this.windowSearchParams.get('engine');
				await this.getVehicle();
			}

			if (this.windowSearchParams.get('plate')) {
				this.searchType = 'license_plate';
				this.licensePlate = this.windowSearchParams.get('plate');
				this.licensePlateState = this.windowSearchParams.get('state');
				await this.decodePlate();
			}

			if (this.windowSearchParams.get('vin')) {
				this.searchType = 'vin';
				this.VIN = this.windowSearchParams.get('vin');
				// await this.decodeVin();
			}

			if (this.windowSearchParams.get('interchange')) {
				this.searchType = 'interchange';
				this.interchange = this.windowSearchParams.get('interchange');
				// await this.getInterchangeParts();
			}

			this.$watch('searchType', (value) => {
				if (value !== 'vehicle') {
					this.vehicle = null;
					this.selections = {
						year: '',
						make: '',
						model: '',
						engine: '',
						category: '',
					};
					this.makes = [];
					this.models = [];
					this.engines = [];
				}

				if (value !== 'vin') this.VIN = '';
			});

			window.addEventListener('set-vehicle', (ev) => {
				this.vehicle = {
					...ev.detail.vehicle,
					displacement_liters: ev.detail.vehicle.engine,
				};

				this.selections = {
					year: this.vehicle.year,
					make: this.vehicle.make,
					model: this.vehicle.model,
					engine: this.vehicle.engine,
					category: '',
				};
			});
		},

		async findHandler() {
			switch (this.searchType) {
				case 'vehicle':
					const selectionsClone = Object.entries(this.selections).reduce(
						(acc, [k, v]) => (v ? { ...acc, [k]: v } : acc),
						{}
					);

					selectionsClone.y = selectionsClone.year;

					delete selectionsClone.year;

					const searchString = new URLSearchParams(selectionsClone).toString();

					window.location = `${
						window.currentLanguageCode ? '/' + window.currentLanguageCode + '/' : '/'
					}products/?${searchString}`;
					return;

				case 'part_number':
					window.location = `${
						window.currentLanguageCode ? '/' + window.currentLanguageCode + '/' : '/'
					}products/?partNumbers=${this.partNumber}`;
					return;

				case 'vin':
					window.location = `${
						window.currentLanguageCode ? '/' + window.currentLanguageCode + '/' : '/'
					}products/?vin=${this.VIN}`;
					return;

				case 'license_plate':
					window.location = `${
						window.currentLanguageCode ? '/' + window.currentLanguageCode + '/' : '/'
					}products/?plate=${this.licensePlate}&state=${this.licensePlateState}`;
					return;

				case 'interchange':
					window.location = `${
						window.currentLanguageCode ? '/' + window.currentLanguageCode + '/' : '/'
					}products/?interchange=${this.interchange}`;
					return;

				default:
					console.log('Nothing to do.');
					break;
			}

			const payload = { partNumbers: this.partsResults.map((p) => p.part_number) };

			window.location =
				this.partsResults.length === 0
					? '/products/?no-results'
					: '/products/?' + new URLSearchParams(payload).toString();
		},

		async postCall(action, data = {}) {
			const formData = new FormData();

			formData.append('action', action);

			for (const [key, value] of Object.entries(data)) {
				formData.append(key, value);
			}

			const fetchEvent = new CustomEvent('fetching', {
				detail: { isFetching: true },
			});

			const fetchEventFalse = new CustomEvent('fetching', {
				detail: { isFetching: false },
			});

			window.dispatchEvent(fetchEvent);

			const response = await fetch('/wp-admin/admin-ajax.php', {
				method: 'POST',
				body: formData,
			});

			const result = await response.json();

			window.dispatchEvent(fetchEventFalse);

			return result;
		},

		async decodeVin() {
			if (this.VIN === '') return;

			const data = await this.postCall('decode_vin', {
				VIN: this.VIN,
			});

			if (data?.Results[0]?.ErrorCode !== '0') {
				this.partNumbers = null;
				this.partsResults = [];
				return;
			}

			this.selections.year = data?.Results[0]?.ModelYear;
			this.selections.make = data?.Results[0]?.Make;
			this.selections.model = data?.Results[0]?.Model;
			this.selections.engine = data?.Results[0]?.DisplacementL;

			await this.getVehicle();

			await this.getParts();
		},

		async decodePlate() {
			if (this.licensePlate === '' || this.licensePlateState === '') return;

			const data = await this.postCall('get_license_plate', {
				plate: this.licensePlate,
				state: this.licensePlateState,
			});

			if (data?.vin) {
				this.VIN = data.vin;

				await this.decodeVin();
			} else {
				this.partsResults = [];
			}
		},

		async getMakes() {
			if (this.selections.year === '') {
				this.makes = [];
				return;
			}

			this.makes = await this.postCall('get_makes', {
				year: this.selections.year,
			});
		},

		async getModels() {
			if (this.selections.year === '' || this.selections.make === '') {
				this.models = [];
				return;
			}

			this.models = await this.postCall('get_models', {
				year: this.selections.year,
				make: this.selections.make,
			});
		},

		async getEngines() {
			if (
				this.selections.year === '' ||
				this.selections.make === '' ||
				this.selections.model === ''
			) {
				this.engines = [];
				return;
			}

			this.engines = await this.postCall('get_engines', {
				year: this.selections.year,
				make: this.selections.make,
				model: this.selections.model,
			});
		},

		async getVehicle() {
			if (
				this.selections.year === '' ||
				this.selections.make === '' ||
				this.selections.model === '' ||
				this.selections.engine === ''
			) {
				this.vehicle = null;
				return;
			}

			const data = await this.postCall('get_vehicle', {
				year: this.selections.year,
				make: this.selections.make,
				model: this.selections.model,
				engine: this.selections.engine,
			});

			if (data.length === 0) {
				this.partsResults = [];

				return;
			}

			if (data !== '' && typeof data[0] !== 'undefined') {
				this.vehicle = data[0];
				this.partNumbers = [
					...data[0]?.coverage_parts.split(','),
					...data[0]?.choice_parts.split(','),
				].filter((p) => p);
			}
		},

		async getParts() {
			if (this.partNumbers === null) {
				return;
			}

			let payload = { part_numbers: this.partNumbers };

			if (this.selections.category !== '') payload.category = this.selections.category;

			this.partsResults = await this.postCall('get_parts', payload);
		},

		async getPart() {
			if (this.partNumber === '') {
				return;
			}

			this.partsResults = await this.postCall('get_part', {
				part_number: this.partNumber,
			});
		},

		async getInterchangeParts() {
			if (this.interchange === '') {
				return;
			}

			this.partsResults = await this.postCall('get_interchange_parts', {
				part_number: this.interchange,
			});
		},
	}));

	Alpine.data('applicationsTab', () => ({
		partNumber: window.currentPartNumber,
		showLoading: false,
		fetching: false,
		page: 1,
		totalPages: null,
		applications: [],

		async init() {
			this.getApplications();
		},

		async postCall(action, data = {}) {
			const formData = new FormData();

			formData.append('action', action);

			for (const [key, value] of Object.entries(data)) {
				formData.append(key, value);
			}

			const response = await fetch('/wp-admin/admin-ajax.php', {
				method: 'POST',
				body: formData,
			});

			return await response.json();
		},

		async getApplications() {
			if (this.fetching) return;

			this.fetching = true;
			this.showLoading = true;

			if (this.page >= this.totalPages && this.totalPages !== null) {
				this.showLoading = false;
				this.fetching = false;
				return;
			}

			const data = await this.postCall('get_paginated_part_applications', {
				page: this.page,
				part_number: this.partNumber,
			});

			this.fetching = false;
			this.showLoading = false;

			this.totalPages = data.total;
			this.applications.push(...data.applications);
			this.page = data.page + 1;
		},
	}));
});
