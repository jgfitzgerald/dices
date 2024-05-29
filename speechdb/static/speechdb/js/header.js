function toggleMobileMenu() {
    var mobileMenu = document.getElementById('mobile-menu-2');
    mobileMenu.classList.toggle('hidden');
}

function toggleDatabaseMenu() {
    var windowWidth = window.innerWidth;
    var databaseMenuSmall = document.getElementById('database-menu-small');
    var databaseMenuLarge = document.getElementById('database-menu-large');
    if (windowWidth < 1024) {
        databaseMenuLarge.classList.add('hidden');
        databaseMenuSmall.classList.toggle('hidden');
    } else {
        databaseMenuSmall.classList.add('hidden');
        databaseMenuLarge.classList.toggle('hidden');
    }
}

window.addEventListener('resize', function() {
    var windowWidth = window.innerWidth;
    if (windowWidth < 1024) {
        var databaseMenuLarge = document.getElementById('database-menu-large');
        databaseMenuLarge.classList.add('hidden');
    } else {
        var databaseMenuSmall = document.getElementById('database-menu-small');
        databaseMenuSmall.classList.add('hidden');
    }
});