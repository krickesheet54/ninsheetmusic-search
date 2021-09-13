<script>
	import { onMount } from "svelte";
	import Sheet from "./Sheet.svelte";

	let query = "";
	let sheets = [];
	let filtered = [];

	async function loadedSheets(r) {
		sheets = await r.json();
	}

	async function fetchSheets() {
		await fetch("/sheets.json").then(loadedSheets);
	}

	// thanks to https://www.davidbcalhoun.com/2019/matching-accented-strings-in-javascript/
	function removeDiacritics(str) {
		return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
	}

	// very simple fuzzy match algorithm
	async function fuzzyMatch(needle, haystack) {
		haystack = removeDiacritics(haystack.toLowerCase());
		let index = 0;

		let setFirst = false;
		let first = 0;

		for (let i = 0; i < haystack.length; i++) {
			if (haystack[i] === needle[index]) {
				if (!setFirst) {
					first = i;
					setFirst = true;
				}
				index++;
			}

			if (index == needle.length) {
				return i - first;
			}
		}

		return -1;
	}

	// TODO: debounce
	async function filter(event) {
		let q = query.toLowerCase()
		if (q.length < 1) {
			filtered = [];
			return;
		}

		filtered = [];
		// run a simple filter
		for (let sheet of sheets) {
			// try on the title
			let len = await fuzzyMatch(q, sheet.title);
			if (len !== -1) {
				sheet.score = len;
				filtered.push(sheet);
			}
			else {
				// try again on the game
				let len = await fuzzyMatch(q, sheet.game);
				if (len !== -1) {
					sheet.score = len;
					filtered.push(sheet);
				}
			}
		}

		// sort
		filtered.sort((a, b) => {
			return a.score - b.score;
		});

		filtered = filtered.slice(0, Math.min(50, filtered.length));
	}

	onMount(fetchSheets);
</script>

<main>
	<h1><a href="https://www.ninsheetmusic.org/">Ninsheetmusic</a> Search</h1>
	<input bind:value={query} on:input={filter} type="search" placeholder="Search..." size=50>

	{#if filtered.length > 0}
	<ul>
		{#each filtered as sheet}
			<Sheet sheet={sheet} />
		{/each}
	</ul>
	{/if}

</main>

<style>
	main {
		padding: 1em;
		margin: 0 auto;
	}

	h1 {
		color: #d63879;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
		margin: 0;
		margin-bottom: 2rem;
	}

	h1 a {
		color: inherit;
	}

	input {
		margin-bottom: 2rem;
	}

	ul {
		list-style: none;
		margin: 0;
		padding: 0;
	}

	@media (max-width: 640px) {
		h1 {
			font-size: 28pt;
		}

		input {
			width: 100%;
		}
	}
</style>
