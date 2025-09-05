import React from "react";

type Props = {
  pepito: any[];
  nextCursor: number | null;
};

export default function DataView({ pepito }: Props) {
  return (
    <>
      <table
        className="table-primary"
        style={{ width: "100%", borderCollapse: "collapse" }}
      >
        <thead>
          <tr>
            <th>NOMBRE</th>
            <th>APELLIDO</th>
            <th>TIPO</th>
            <th>EMAIL</th>
          </tr>
        </thead>
        <tbody>
          {" "}
          {data.map((user) => (
            <tr key={user.id}>
              <td>{user.first_name}</td>
              <td>{user.last_name}</td>
              <td>{user.type}</td>
              <td>{user.email}</td>
            </tr>
          ))}
        </tbody>
      </table>{" "}
      <div>{nextCursor}</div>
    </>
  );
}

export default DataView;
