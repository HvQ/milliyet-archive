<script>
  export let newspapers = [];
  export let date = '';
  
  function viewNewspaper(id, name) {
    const encodedName = encodeURIComponent(name);
    window.location.href = `/viewer?id=${id}&name=${encodedName}&date=${date}`;
  }
</script>

<div class="newspaper-list">
  <h2 class="text-xl font-semibold mb-4">Available Newspapers ({newspapers.length})</h2>
  
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {#each newspapers as newspaper}
      <div class="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow">
        <h3 class="text-lg font-medium mb-2">{newspaper.name}</h3>
        
        <div class="flex justify-between items-center mt-4">
          <span class="text-sm text-gray-500">{date}</span>
          
          <button 
            class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded"
            on:click={() => viewNewspaper(newspaper.id, newspaper.name)}
          >
            View
          </button>
        </div>
      </div>
    {/each}
  </div>
</div>