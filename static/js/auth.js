// modulo de autenticacion
export const AuthService = {
    async login(username, password) {
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const result = await response.json();

            if (result.success) {
                localStorage.setItem('userSession', JSON.stringify({
                    username: username,
                    nombre: result.user,
                    rol: result.rol,
                    loggedIn: true,
                    timestamp: new Date().toISOString()
                }));
                return { success: true, message: "Acceso concedido" };
            } else {
                return { success: false, message: result.message };
            }
        } catch (error) {
            console.error('Error:', error);
            return { success: false, message: "Error de conexión" };
        }
    },

    logout() {
        localStorage.removeItem('userSession');
        sessionStorage.clear();
    },

    isAuthenticated() {
        const session = localStorage.getItem('userSession');
        if (!session) return false;
        try {
            const data = JSON.parse(session);
            return data.loggedIn === true;
        } catch {
            return false;
        }
    },

    getCurrentUser() {
        const session = localStorage.getItem('userSession');
        if (!session) return null;
        try {
            return JSON.parse(session);
        } catch {
            return null;
        }
    }
};

export function redirectToMain() {
    const mainPath = '/main-form';
    window.location.href = mainPath;
}

export function requireAuth() {
    if (!AuthService.isAuthenticated()) {
        window.location.href = '/';
        return false;
    }
    return true;
}