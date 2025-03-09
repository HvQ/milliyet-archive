<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { browser } from '$app/environment';
  
  let pdfUrl = '';
  let newspaperName = '';
  let loading = true;
  let error = null;
  
  onMount(async () => {
    if (browser) {
      try {
        const searchParams = new URLSearchParams($page.url.search);
        const id = searchParams.get('id');
        const name = searchParams.get('name');
        const date = searchParams.get('date');
        
        if (!id || !name || !date) {
          throw new Error('Missing required parameters');
        }
        
        newspaperName = decodeURIComponent(name);
        loading = true;
        
        const response = await fetch('/api/download', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id, name: newspaperName, date })
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to download newspaper');
        }
        
        const data = await response.json();
        
        if (data.pdf_data) {
          // Create blob from base64 data
          const byteCharacters = atob(data.pdf_data);
          const byteNumbers = new Array(byteCharacters.length);
          
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }
          
          const byteArray = new Uint8Array(byteNumbers);
          const blob = new Blob([byteArray], { type: 'application/pdf' });
          
          // Create object URL for the PDF viewer
          pdfUrl = URL.createObjectURL(blob);
        } else {
          throw new Error('No PDF data received');
        }
      } catch (err) {
        error = err.message;
      } finally {
        loading = false;
      }
    }
  });
  
  function goBack() {
    history.back();
  }
</script>

<main class="container mx-auto px-4 py-8">
  <div class="flex items-center justify-between mb-6">
    <button 
      class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-4 rounded inline-flex items-center"
      on:click={goBack}
    >
      <span class="mr-1">←</span> Back
    </button>
    
    {#if newspaperName}
      <h1 class="text-2xl font-bold">{newspaperName}</h1>
    {/if}
  </div>
  
  {#if loading}
    <div class="text-center py-20">
      <div class="inline-block animate-spin h-10 w-10 border-4 border-gray-300 border-t-blue-600 rounded-full"></div>
      <p class="mt-4">Loading newspaper...</p>
      <p class="text-sm text-gray-500 mt-2">This may take a few moments</p>
    </div>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
      <strong class="font-bold">Error:</strong>
      <span class="block sm:inline">{error}</span>
    </div>
  {:else if pdfUrl}
    <div class="h-screen">
      <iframe 
        title="PDF Viewer" 
        src={pdfUrl} 
        class="w-full h-full border rounded"
        frameborder="0"
      ></iframe>
    </div>
  {/if}
</main>