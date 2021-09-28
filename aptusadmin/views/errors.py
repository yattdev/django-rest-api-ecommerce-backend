from django.shortcuts import render


# Error Pages
def permission_denied(request):
    template = 'errors/inspinia_403.html'
    app_name = request.get_full_path().split('/')[1]
    if app_name in ['enseignant', 'espaceetudiant']:
        template = 'errors/coreui_403.html'
    return render(request, template,{'active_accueil':True})


def server_error(request):
    template = 'errors/inspinia_500.html'
    app_name = request.get_full_path().split('/')[1]
    if app_name in ['enseignant', 'espaceetudiant']:
        template = 'errors/coreui_500.html'
    return render(request, template,{'active_accueil':True})


def not_found(request):
    template = 'errors/inspinia_404.html'
    app_name = request.get_full_path().split('/')[1]
    if app_name in ['enseignant', 'espaceetudiant']:
        template = 'errors/coreui_404.html'
    return render(request, template,{'active_accueil':True})


def bad_request(request):
    template = 'errors/inspinia_400.html'
    app_name = request.get_full_path().split('/')[1]
    if app_name in ['enseignant', 'espaceetudiant']:
        template = 'errors/coreui_400.html'
    return render(request, template,{'active_accueil':True})
