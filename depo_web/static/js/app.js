// Flash mesajlarını 4 saniye sonra gizle
document.addEventListener('DOMContentLoaded', () => {
  const flash = document.querySelector('.flash-bar');
  if (flash) {
    setTimeout(() => {
      flash.style.transition = 'opacity .4s';
      flash.style.opacity = '0';
      setTimeout(() => flash.remove(), 400);
    }, 4000);
  }
});
