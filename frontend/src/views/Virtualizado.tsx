import React, { useCallback, useState } from "react";

type Props = {};

function Virtualizado({}: Props) {
  console.log("Renderizando Virtualizado");
  const [count, setCount] = useState(0);

  // esta funcion se "redefine" en cada render
  // => nueva referencia en memoria
  const handleClick = useCallback(() => {
    setCount(count + 1); // Acumulador
  }, []);

  return (
    <div className="conteiner m-5">
      <h2>Virtualizado</h2>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Incrementar</button>
    </div>
  );
}

export default Virtualizado;
