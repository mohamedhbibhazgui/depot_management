// ============================================================
// This file is loaded with type="text/babel" in employees.html,
// so JSX (the HTML-looking syntax below) works without a build step.
// Babel converts it to plain JS in the browser.
// ============================================================

const { useState, useEffect } = React;

// A single employee card. Receives data + a delete handler as "props"
// (props = the arguments you pass into a component, like function arguments).
function EmployeeCard({ employee, onDelete }) {
    const initial = employee.name ? employee.name[0].toUpperCase() : "?";

    return (
        <div className="employee-card">
            <div className="card-header">
                <div className="avatar">{initial}</div>
                <div>
                    <div className="name">{employee.name} {employee.fname}</div>
                    <div className="type">{employee.type}</div>
                </div>
            </div>
            <div className="card-body">
                <div>📞 {employee.gsm}</div>
                <div>📍 {employee.adr}</div>
                <div>⚧ {employee.gender}</div>
            </div>
            <div className="card-actions">
                <a href={`/employee/edit_employee/${employee.id}`}>Edit</a>
                <button className="delete" onClick={() => onDelete(employee.id)}>
                    Delete
                </button>
            </div>
        </div>
    );
}

// The main component: owns the data (state), fetches it, filters it,
// and renders the search bar + grid of cards.
function EmployeeApp() {
    // "state" = data that changes over time and should trigger a re-render
    // when it changes. useState gives us [currentValue, functionToUpdateIt].
    const [employees, setEmployees] = useState([]);   // full list from the server
    const [search, setSearch] = useState("");          // what's typed in the search box
    const [loading, setLoading] = useState(true);

    // useEffect runs side effects (like fetching data) after the component
    // renders. The empty array [] at the end means "only run this once,
    // when the component first mounts" (not on every re-render).
    useEffect(() => {
        fetch(window.API_CONFIG.employeesUrl)
            .then(res => res.json())
            .then(data => {
                setEmployees(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load employees:", err);
                setLoading(false);
            });
    }, []);

    function handleDelete(id) {
        if (!confirm("Delete this employee?")) return;

        fetch(`${window.API_CONFIG.employeesUrl}/${id}`, { method: "DELETE" })
            .then(res => {
                if (!res.ok) throw new Error("Delete failed");
                // Remove the deleted employee from local state so the card
                // disappears immediately, without re-fetching the whole list.
                setEmployees(prev => prev.filter(e => e.id !== id));
            })
            .catch(err => alert(err.message));
    }

    // Filter is recalculated on every render based on the current search
    // text — no extra state needed for "filtered list", we derive it.
    const filtered = employees.filter(e => {
        const haystack = `${e.name} ${e.fname} ${e.type} ${e.gsm}`.toLowerCase();
        return haystack.includes(search.toLowerCase());
    });

    if (loading) return <p>Loading employees...</p>;

    return (
        <div>
            <input
                type="text"
                className="search-bar"
                placeholder="Search by name, type, or phone..."
                value={search}
                onChange={e => setSearch(e.target.value)}
            />

            <p className="result-count">
                Showing {filtered.length} of {employees.length} employees
            </p>

            {filtered.length === 0 ? (
                <div className="empty-state">No employees match your search.</div>
            ) : (
                <div className="card-grid">
                    {filtered.map(emp => (
                        <EmployeeCard key={emp.id} employee={emp} onDelete={handleDelete} />
                    ))}
                </div>
            )}
        </div>
    );
}

// Mount the whole thing into the <div id="employee-root"> from the HTML.
const root = ReactDOM.createRoot(document.getElementById("employee-root"));
root.render(<EmployeeApp />);
