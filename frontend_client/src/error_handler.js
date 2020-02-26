const error_handler = {
    run : function($swal, error) {console.log('TESTINGS'); console.log(error);
        var title, description;
        switch(error) {
            case 'INVALID_CREDENTIALS':
                title = 'Invalid Username and/or password.';
                description = 'Please Try Again';
                break;
            case 'NO_APPLICATION_SETTINGS':
                title = 'Server Temporarily Unavailable';
                description = 'Unable to retrieve Application Settings from the Server.';
                break;
            default:
                title = (error.title) ? error.title : 'Error';
                description = (error.description) ? error.description : "<br /><small> "+ error + "</small>";
                break;
        }

        $swal({type: "error", title: title, html : description});
    }
};

export default error_handler;