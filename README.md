# Simulador CI/CD (Taller)

Proyecto individual en **Python + Streamlit** que implementa un simulador de pipeline de Integración y Despliegue usando:

- **POO**
- **Listas**
- **Pilas (LIFO)**
- **Colas (FIFO)**

## Estructura

- `app.py`: Frontend en Streamlit.
- `backend/models.py`: Entidades y enums del dominio (`Job`, `StageResult`, estados y etapas).
- `backend/data_structures.py`: Implementaciones propias de `Stack` y `Queue` usando listas.
- `backend/pipeline.py`: Lógica principal del simulador (`CICDPipeline`).


## Instalación

1. Crear entorno virtual (opcional).
2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Ejecutar:

   ```bash
   streamlit run app.py
   ```

## Flujo

1. Encolar trabajos con datos del repositorio.
2. Procesar siguiente trabajo (cola FIFO).
3. Si compila, prueba y despliega con éxito, se guarda en historial (pila LIFO).
4. Aplicar rollback al último despliegue exitoso.
