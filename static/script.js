$(document).ready(function() {
    $("a.mozapp").click(function(e) {
        e.preventDefault();
        console.log('Installing web app');
        window.navigator.mozApps.install(this.href);
    });
    $("a.packagedmozapp").click(function(e) {
        e.preventDefault();
        console.log('Installing packaged app');
        window.navigator.mozApps.installPackage(this.href);
    });
    $("#installurl").focus();
});