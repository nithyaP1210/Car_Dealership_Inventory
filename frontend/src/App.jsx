import { useEffect, useState } from "react";

const API = "http://localhost:8000";

const emptyVehicle = {
  make: "",
  model: "",
  category: "",
  price: "",
  quantity: "",
};

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [role, setRole] = useState(localStorage.getItem("role"));
  const [name, setName] = useState(localStorage.getItem("name") || "");
  const [mode, setMode] = useState("login");
  const [message, setMessage] = useState("");
  const [vehicles, setVehicles] = useState([]);
  const [form, setForm] = useState(emptyVehicle);
  const [editingId, setEditingId] = useState(null);
  const [search, setSearch] = useState({
    make: "",
    model: "",
    category: "",
    min_price: "",
    max_price: "",
  });

  const [authForm, setAuthForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  useEffect(() => {
    if (token) loadVehicles();
  }, [token]);

  async function request(path, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };
    if (token) headers.Authorization = `Bearer ${token}`;

    const response = await fetch(API + path, { ...options, headers });
    const data = await response.json().catch(() => ({}));

    if (!response.ok) throw new Error(data.detail || "Request failed");
    return data;
  }

  async function register(e) {
    e.preventDefault();
    try {
      const data = await request("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(authForm),
      });
      setMessage(`Registered successfully. Your role is ${data.role}.`);
      setMode("login");
    } catch (error) {
      setMessage(error.message);
    }
  }

  // FIXED: backend's /api/auth/login uses OAuth2PasswordRequestForm,
  // which expects application/x-www-form-urlencoded with a "username"
  // field (not JSON with "email"). This bypasses the shared request()
  // helper since that always sends JSON.
  async function login(e) {
    e.preventDefault();
    try {
      const body = new URLSearchParams();
      body.set("username", authForm.email);
      body.set("password", authForm.password);

      const response = await fetch(API + "/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body.toString(),
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) throw new Error(data.detail || "Login failed");

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("role", data.role);
      localStorage.setItem("name", data.name);
      setToken(data.access_token);
      setRole(data.role);
      setName(data.name);
      setMessage("");
    } catch (error) {
      setMessage(error.message);
    }
  }

  function logout() {
    localStorage.clear();
    setToken(null);
    setRole(null);
    setName("");
    setVehicles([]);
  }

  async function loadVehicles() {
    try {
      setVehicles(await request("/api/vehicles"));
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function searchVehicles() {
    const params = new URLSearchParams();
    Object.entries(search).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });

    try {
      setVehicles(await request(`/api/vehicles/search?${params.toString()}`));
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function purchase(id) {
    try {
      await request(`/api/vehicles/${id}/purchase`, { method: "POST" });
      await loadVehicles();
      setMessage("Vehicle purchased.");
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function saveVehicle(e) {
    e.preventDefault();

    const payload = {
      ...form,
      price: Number(form.price),
      quantity: Number(form.quantity),
    };

    try {
      if (editingId) {
        await request(`/api/vehicles/${editingId}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
        setMessage("Vehicle updated.");
      } else {
        await request("/api/vehicles", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        setMessage("Vehicle added.");
      }

      setForm(emptyVehicle);
      setEditingId(null);
      await loadVehicles();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function deleteVehicle(id) {
    if (!window.confirm("Delete this vehicle?")) return;
    try {
      await request(`/api/vehicles/${id}`, { method: "DELETE" });
      await loadVehicles();
      setMessage("Vehicle deleted.");
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function restock(id) {
    const quantity = Number(window.prompt("How many vehicles to add?", "1"));
    if (!quantity || quantity < 1) return;

    try {
      await request(`/api/vehicles/${id}/restock`, {
        method: "POST",
        body: JSON.stringify({ quantity }),
      });
      await loadVehicles();
      setMessage("Vehicle restocked.");
    } catch (error) {
      setMessage(error.message);
    }
  }

  function editVehicle(vehicle) {
    setEditingId(vehicle.id);
    setForm({
      make: vehicle.make,
      model: vehicle.model,
      category: vehicle.category,
      price: vehicle.price,
      quantity: vehicle.quantity,
    });
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="mb-8 text-center">
            <p className="text-cyan-400 font-semibold tracking-widest">DRIVEHUB</p>
            <h1 className="text-4xl font-bold mt-2">Car Inventory</h1>
            <p className="text-slate-400 mt-2">Simple dealership inventory management.</p>
          </div>

          <form
            onSubmit={mode === "login" ? login : register}
            className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl"
          >
            <h2 className="text-2xl font-bold mb-5">
              {mode === "login" ? "Welcome back" : "Create account"}
            </h2>

            {mode === "register" && (
              <input
                className="input"
                placeholder="Full name"
                value={authForm.name}
                onChange={(e) => setAuthForm({ ...authForm, name: e.target.value })}
                required
              />
            )}

            <input
              className="input"
              placeholder="Email"
              type="email"
              value={authForm.email}
              onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
              required
            />

            <input
              className="input"
              placeholder="Password (6+ characters)"
              type="password"
              value={authForm.password}
              onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
              required
            />

            <button className="w-full bg-cyan-400 text-slate-950 font-bold py-3 rounded-xl mt-3 hover:bg-cyan-300">
              {mode === "login" ? "LOGIN" : "REGISTER"}
            </button>

            <button
              type="button"
              className="w-full text-slate-400 mt-4 text-sm"
              onClick={() => setMode(mode === "login" ? "register" : "login")}
            >
              {mode === "login"
                ? "New here? Create an account"
                : "Already have an account? Login"}
            </button>

            {message && <p className="text-red-400 mt-4 text-sm">{message}</p>}
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 bg-slate-950/95 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <p className="text-cyan-400 font-bold tracking-widest">DRIVEHUB</p>
            <p className="text-xs text-slate-500">Inventory System</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-300">
              {name} · {role}
            </span>
            <button onClick={logout} className="border border-slate-700 px-4 py-2 rounded-lg text-sm">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-10">
        <section className="mb-8">
          <p className="text-cyan-400 font-semibold">AVAILABLE VEHICLES</p>
          <h1 className="text-4xl md:text-5xl font-bold mt-2">Find your next drive.</h1>
          <p className="text-slate-400 mt-3">Search, purchase and manage dealership inventory.</p>
        </section>

        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-5 mb-8">
          <div className="grid md:grid-cols-5 gap-3">
            {["make", "model", "category", "min_price", "max_price"].map((key) => (
              <input
                key={key}
                className="input"
                placeholder={key.replace("_", " ")}
                value={search[key]}
                onChange={(e) => setSearch({ ...search, [key]: e.target.value })}
              />
            ))}
          </div>
          <div className="flex gap-3 mt-4">
            <button onClick={searchVehicles} className="btn-primary">Search</button>
            <button onClick={loadVehicles} className="btn-secondary">Clear</button>
          </div>
        </section>

        {message && (
          <div className="bg-cyan-400/10 border border-cyan-400/30 text-cyan-200 rounded-xl p-3 mb-6">
            {message}
          </div>
        )}

        <section className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {vehicles.map((vehicle) => (
            <article key={vehicle.id} className="bg-white text-slate-900 rounded-2xl overflow-hidden shadow-xl">
              <div className="h-28 bg-gradient-to-br from-slate-800 to-slate-600 flex items-end p-5">
                <span className="text-white text-sm bg-black/30 px-3 py-1 rounded-full">
                  {vehicle.category}
                </span>
              </div>
              <div className="p-5">
                <p className="text-sm text-slate-500">{vehicle.make}</p>
                <h2 className="text-2xl font-bold">{vehicle.model}</h2>
                <p className="text-xl font-semibold mt-3">${vehicle.price.toLocaleString()}</p>
                <p className={`text-sm mt-1 ${vehicle.quantity ? "text-emerald-600" : "text-red-600"}`}>
                  {vehicle.quantity ? `${vehicle.quantity} in stock` : "Out of stock"}
                </p>

                <button
                  disabled={vehicle.quantity === 0}
                  onClick={() => purchase(vehicle.id)}
                  className="w-full mt-4 py-3 rounded-xl font-bold disabled:bg-slate-200 disabled:text-slate-400 bg-slate-900 text-white hover:bg-slate-700"
                >
                  {vehicle.quantity === 0 ? "SOLD OUT" : "PURCHASE"}
                </button>

                {role === "ADMIN" && (
                  <div className="grid grid-cols-3 gap-2 mt-3">
                    <button className="small-btn" onClick={() => editVehicle(vehicle)}>Edit</button>
                    <button className="small-btn" onClick={() => restock(vehicle.id)}>Restock</button>
                    <button className="small-btn text-red-600" onClick={() => deleteVehicle(vehicle.id)}>Delete</button>
                  </div>
                )}
              </div>
            </article>
          ))}
        </section>

        {role === "ADMIN" && (
          <section className="mt-10 bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 className="text-2xl font-bold mb-5">
              {editingId ? "Update Vehicle" : "Add Vehicle"}
            </h2>
            <form onSubmit={saveVehicle} className="grid md:grid-cols-5 gap-3">
              {["make", "model", "category", "price", "quantity"].map((key) => (
                <input
                  key={key}
                  className="input"
                  placeholder={key}
                  type={key === "price" || key === "quantity" ? "number" : "text"}
                  value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                  required
                />
              ))}
              <div className="md:col-span-5 flex gap-3">
                <button className="btn-primary">{editingId ? "Save Changes" : "Add Vehicle"}</button>
                {editingId && (
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => {
                      setEditingId(null);
                      setForm(emptyVehicle);
                    }}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </section>
        )}

        <p className="text-center text-slate-600 text-sm mt-12">
          Car Dealership Inventory System · FastAPI + SQLite + React + Tailwind
        </p>
      </main>
    </div>
  );
}