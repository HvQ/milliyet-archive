<script>
  import '../app.css';
</script>

<div class="min-h-screen bg-gray-50">
  <header class="bg-blue-600 text-white shadow">
    <div class="container mx-auto px-4 py-4">
      <div class="flex justify-between items-center">
        <a href="/" class="text-xl font-bold">Milliyet Archive</a>
        <div>
          <a href="https://gazetearsivi.milliyet.com.tr/" target="_blank" class="text-white hover:text-blue-200">
            Official Archive
          </a>
        </div>
      </div>
    </div>
  </header>

  <slot />

  <footer class="bg-gray-100 mt-10">
    <div class="container mx-auto px-4 py-6">
      <p class="text-center text-gray-600 text-sm">
        © 2025 Milliyet Archive Viewer. This is an unofficial viewer.
      </p>
    </div>
  </footer>
</div>