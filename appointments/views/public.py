"""
Vistas públicas (accesibles sin autenticación)
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Especialidad, Medico, ConfiguracionSistema
from ..forms import RegistroPacienteForm


def inicio(request):
    """Página de bienvenida"""
    especialidades = Especialidad.objects.filter(activo=True)
    medicos = Medico.objects.filter(activo=True).select_related('usuario')[:6]
    config = ConfiguracionSistema.get_configuracion()
    
    context = {
        'especialidades': especialidades,
        'medicos': medicos,
        'config': config,
    }
    return render(request, 'inicio.html', context)


def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a {user.get_full_name()}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('inicio')


def registro_paciente(request):
    """Registro de nuevo paciente"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistroPacienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido/a a MediTurnos.')
            return redirect('paciente_dashboard')
    else:
        form = RegistroPacienteForm()
    
    return render(request, 'registro.html', {'form': form})


@login_required
def dashboard(request):
    """Redirige al dashboard según el rol del usuario"""
    if request.user.rol == 'admin':
        return redirect('admin_dashboard')
    elif request.user.rol == 'medico':
        return redirect('medico_dashboard')
    elif request.user.rol == 'paciente':
        return redirect('paciente_dashboard')
    else:
        messages.error(request, 'No tienes un rol asignado.')
        return redirect('inicio')
