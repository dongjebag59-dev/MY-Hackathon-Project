
/* ==========================================================================
   index.html - 배경 이미지 슬라이더
   ========================================================================== */

function initSlider() {
    const images = document.querySelectorAll('.slider-img');
    if (images.length === 0) return;

    let currentIndex = 0;
    setInterval(() => {
        images[currentIndex].classList.remove('opacity-100');
        images[currentIndex].classList.add('opacity-0');
        currentIndex = (currentIndex + 1) % images.length;
        images[currentIndex].classList.remove('opacity-0');
        images[currentIndex].classList.add('opacity-100');
    }, 4000);
}

window.addEventListener("DOMContentLoaded", () => {
    initSlider();
});
