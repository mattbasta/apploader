function canInstall(manifest) {
    var callback = null;
    var fired = false;
    var success = function(cb) {
        if (fired) {
            cb();
            return;
        }
        callback = cb;
    };
    var request;
    try {
        request = navigator.mozApps.checkInstalled(manifest);
    } catch(e) {
        fired = true;
        return success;
    }
    request.onerror = function() {
        alert('Error: ' + this.error.message);
    };
    request.onsuccess = function() {
        if (callback) {
            callback();
        } else {
            fired = true;
        }
    };

    return success;
}

function errors(request) {
    request.onerror = function() {
        alert('Error: ' + this.error.name);
    };
}

$(document).ready(function() {
    $("a.mozapp").click(function(e) {
        e.preventDefault();
        console.log('Installing web app');
        var href = this.href;
        canInstall(this.href)(function() {
            errors(window.navigator.mozApps.install(href));
        });
    });
    $("a.packagedmozapp").click(function(e) {
        e.preventDefault();
        console.log('Installing packaged app');
        var href = this.href;
        canInstall(this.href)(function() {
            errors(window.navigator.mozApps.installPackage(href));
        });
    });
    $("#installurl").focus();
});
