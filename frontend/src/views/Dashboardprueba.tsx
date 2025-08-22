import { useEffect, useState } from "react";

function Dashboard() {
  const userName = JSON.parse(localStorage.getItem("user") || "{}").first_name;

  const BACKEND_IP = "localhost";
  const BACKEND_PORT = "8000";
  const ENDPOINT = "users/paginate";
  const API_URL = `http://${BACKEND_IP}:${BACKEND_PORT}/${ENDPOINT}`;

  type User = { ide: number; username: string; [key: string]: any };
  const [data, setData] = useState<User[]>([]);

  const [nextCursor, setNextCursor] = useState<number | null>(null);

  function mostrar_datos(data: any) {
    console.log("data", data);
    if (!data.message) setData(data);
    else setData([]);
  }

  function getUsers(last_seen_id: number | null) {
    const token = localStorage.getItem("token");
    var myHeaders = new Headers();
    myHeaders.append("Authorization", `Bearer ${token}`);
    myHeaders.append("Content-Type", "application/json");

    const raw = JSON.stringify({
      limit: 5,
      last_seen_id: last_seen_id,
    });

    const requestOptions = {
      method: "POST",
      headers: myHeaders,
      body: raw,
    };

    fetch(API_URL, requestOptions)
      .then((respond) => respond.json())
      .then((response) => {
        if (response.message) {
          setData([]);
          setNextCursor(null);
          return;
        }
        const newData = last_seen_id
          ? [...data, ...response.users]
          : response.users;

        setData(newData);
        setNextCursor(response.next_cursor);
      })
      .catch((error) => console.log("error", error));
  }
  // Función para el botón "Recargar datos"
  function handleReload() {
    getUsers(null);
  }

  // Función para el botón "Cargar más"
  function handleLoadMore() {
    getUsers(nextCursor);
  }

  useEffect(() => {
    // Carga inicial de datos
    handleReload();
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      <div>Bienvenido {userName}!</div>
      <table className="table-primary">
        <thead>
          <td>NOMRBE</td>
          <td>APELLIDO</td>
          <td>TIPO</td>
          <td>EMAIL</td>
        </thead>
        <tbody>
          {data.map((pepe) => {
            return (
              <tr key={pepe.id}>
                <td>{pepe.first_name}</td>
                <td>{pepe.last_name}</td>
                <td>{pepe.type}</td>
                <td>{pepe.email}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <div>
        <button onClick={get_users_all}>Recargar datos</button>
      </div>
    </div>
  );
}

export default Dashboard;
