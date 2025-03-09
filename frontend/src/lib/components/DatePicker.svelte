<script>
  import { dateStore } from '$lib/stores/dateStore';
  import dayjs from 'dayjs';
  
  let dateInput = '';
  
  function formatDate(date) {
    const formattedDate = dayjs(date).format('YYYY.MM.DD');
    dateStore.set(formattedDate);
    return formattedDate;
  }
  
  function handleInput(event) {
    const inputDate = event.target.value;
    if (inputDate) {
      dateInput = inputDate;
      formatDate(inputDate);
    }
  }
  
  function isValidDate(date) {
    return dayjs(date).isValid();
  }
  
  $: {
    if ($dateStore && !dateInput) {
      // Convert from YYYY.MM.DD to YYYY-MM-DD for the input field
      dateInput = $dateStore.replace(/\./g, '-');
    }
  }
</script>

<div class="date-picker">
  <label for="date-input" class="block text-sm font-medium text-gray-700 mb-1">
    Select a Date
  </label>
  
  <div class="relative">
    <input
      id="date-input"
      type="date"
      class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 
        focus:outline-none focus:ring-blue-500 focus:border-blue-500"
      value={dateInput}
      on:input={handleInput}
    />
    
    {#if $dateStore}
      <div class="mt-2 text-sm text-gray-500">
        Current search: <span class="font-medium">{$dateStore}</span>
      </div>
    {/if}
  </div>
</div>