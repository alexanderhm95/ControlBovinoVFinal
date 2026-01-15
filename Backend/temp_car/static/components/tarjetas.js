document.addEventListener('DOMContentLoaded', function() {
    function actualizarDatos(contenedorId, collarId) {
        fetch('/ultimo/registro/' + collarId)
            .then(response => {
                if (response.status !== 200) {
                    throw new Error('Error al obtener datos');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    document.getElementById(contenedorId).innerHTML = 
                    `<br><br><br><br><br>
                    <i class="bi bi-exclamation-triangle"></i> Datos no disponibles`;
                } else {
                    // Actualiza el contenido del reloj
                    document.getElementById(contenedorId).innerHTML = 
                    `<strong>Nombre:</strong> ${data.nombre_vaca || ''} <br>
                    <strong>Temperatura:</strong> ${data.temperatura || ''}°C <br> 
                    <strong>Pulsaciones:</strong> ${data.pulsaciones || ''} bpm <br> 
                    <strong>Fecha control:</strong> ${data.fecha_lectura || ''} ${data.hora_lectura || ''}`;
                }
            })
            .catch(error => {
                document.getElementById(contenedorId).innerHTML = 
                `<br> <br><br><br><br>
                <i class="bi bi-exclamation-triangle"></i> Datos no disponibles`;
            });
    }

    // Llama a actualizarDatos cada 5 segundos
    setInterval(() => {
           }, 5000); // 5 segundos
});
