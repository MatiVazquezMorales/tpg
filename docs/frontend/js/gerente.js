document.addEventListener("DOMContentLoaded", function () {
  const sidebarLinks = document.querySelectorAll('.sidebar .nav-link');

  sidebarLinks.forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      const href = this.getAttribute('href');
      if (href && href !== "#") {
        window.location.href = href;
      }
    });

    const currentPage = location.pathname.split("/").pop();
    if (link.getAttribute('href') === currentPage) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
});
