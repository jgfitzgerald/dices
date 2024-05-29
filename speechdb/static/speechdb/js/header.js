function toggleMobileMenu() {
    var mobileMenu = document.getElementById('mobile-menu-2');
    mobileMenu.classList.toggle('tw-hidden');
}

function toggleDatabaseMenu() {
    var windowWidth = window.innerWidth;
    var databaseMenuSmall = document.getElementById('database-menu-small');
    var databaseMenuLarge = document.getElementById('database-menu-large');
    if (windowWidth < 1024) {
        databaseMenuLarge.classList.add('tw-hidden');
        databaseMenuSmall.classList.toggle('tw-hidden');
    } else {
        databaseMenuSmall.classList.add('tw-hidden');
        databaseMenuLarge.classList.toggle('tw-hidden');
    }
}

window.addEventListener('resize', function() {
    var windowWidth = window.innerWidth;
    if (windowWidth < 1024) {
        var databaseMenuLarge = document.getElementById('database-menu-large');
        databaseMenuLarge.classList.add('tw-hidden');
    } else {
        var databaseMenuSmall = document.getElementById('database-menu-small');
        databaseMenuSmall.classList.add('tw-hidden');
    }
});