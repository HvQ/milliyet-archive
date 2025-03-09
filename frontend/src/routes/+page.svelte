<script>
  import { onMount } from 'svelte';
  import { dateStore } from '$lib/stores/dateStore';
  import DatePicker from '$lib/components/DatePicker.svelte';
  import NewspaperList from '$lib/components/NewspaperList.svelte';
  
  let searchResults = [];
  let loading = false;
  let error = null;
  
  async function searchNewspapers(date) {
    loading = true;
    error = null;
    
    try {
      // Use the full backend URL in production
      const apiUrl = import.meta.env.PROD 
        ? 'https://milliyet-archive.onrender.com/api/search' 
        : '/api/search';
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date })
      });
      
      if (!response.ok) {
        try {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to search newspapers');
        } catch (e) {
          // If parsing JSON fails, it's likely an HTML response
          throw new Error('Server returned an invalid response. API might be unavailable.');
        }
      }
      
      const data = await response.json();
      searchResults = data.newspapers || [];
    } catch (err) {
      error = err.message;
      searchResults = [];
    } finally {
      loading = false;
    }
  }
  
  $: if ($dateStore) {
    searchNewspapers($dateStore);
  }
  
  onMount(() => {
    // Set default date to today in YYYY.MM.DD format
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    dateStore.set(`${year}.${month}.${day}`);
  });
</script>

<main class="container mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-center mb-8">Milliyet Archive</h1>
  
  <div class="max-w-md mx-auto mb-8">
    <DatePicker />
  </div>
  
  {#if loading}
    <div class="text-center py-8">
      <div class="inline-block animate-spin h-8 w-8 border-4 border-gray-300 border-t-blue-600 rounded-full"></div>
      <p class="mt-2">Searching archives...</p>
    </div>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative max-w-md mx-auto">
      <strong class="font-bold">Error:</strong>
      <span class="block sm:inline">{error}</span>
    </div>
  {:else if searchResults.length === 0}
    <div class="text-center py-8 text-gray-600">
      <p>No newspapers found for this date. Try another date.</p>
    </div>
  {:else}
    <NewspaperList newspapers={searchResults} date={$dateStore} />
  {/if}
</main>

<style>
  :global(body) {
    background-color: #f9fafb;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
      Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  }
</style>