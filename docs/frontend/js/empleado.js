document.addEventListener("DOMContentLoaded", function () {
  const sidebarLinks = document.querySelectorAll('.sidebar .menu a');

  const currentPage = location.pathname.split("/").pop();

  sidebarLinks.forEach(link => {
    const href = link.getAttribute('href');

    if (href === currentPage) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }

    link.addEventListener('click', function (e) {
      if (href && href !== "#") {
        e.preventDefault();
        window.location.href = href;
      }
    });
  });
});
