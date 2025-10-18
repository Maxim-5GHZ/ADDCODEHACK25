import React from 'react';

function FieldForm({ fieldType, fieldName, setFieldName, radius, setRadius, area }) {
  return (
    <div className="space-y-4 md:space-y-6">
      <div>
        <label className="block text-lg md:text-xl lg:text-2xl font-semibold mb-2 text-[var(--neutral-dark-color)]" htmlFor="fieldName">
          Название поля
        </label>
        <input
          id="fieldName"
          type="text"
          value={fieldName}
          onChange={(e) => setFieldName(e.target.value)}
          className="w-full rounded-3xl md:rounded-4xl px-4 md:px-6 py-3 md:py-4 text-lg md:text-xl bg-[var(--neutral-light-color)] shadow-2xs focus:outline-0 focus:ring-2 focus:ring-[var(--accent-color)] cursor-text"
          placeholder="Введите название поля"
        />
      </div>

      {fieldType === 'point' && (
        <div>
          <label className="block text-lg md:text-xl lg:text-2xl font-semibold mb-2 text-[var(--neutral-dark-color)]" htmlFor="radius">
            Радиус (метры)
          </label>
          <input
            id="radius"
            type="number"
            value={radius}
            onChange={(e) => setRadius(parseInt(e.target.value) || 100)}
            className="w-full rounded-3xl md:rounded-4xl px-4 md:px-6 py-3 md:py-4 text-lg md:text-xl bg-[var(--neutral-light-color)] shadow-2xs focus:outline-0 focus:ring-2 focus:ring-[var(--accent-color)] cursor-text"
            placeholder="Введите радиус"
            min="1"
          />
        </div>
      )}

      {area && (
        <div className="bg-green-50 p-3 md:p-4 rounded-lg md:rounded-xl border border-green-200">
          <p className="text-base md:text-lg font-semibold text-green-800">
            Площадь: {area}
          </p>
        </div>
      )}

      {fieldType === 'polygon' && (
        <div className="text-base md:text-lg text-gray-600 bg-yellow-50 p-3 md:p-4 rounded-lg md:rounded-xl">
          <p>ℹ️ Выберите на карте от 3 до 5 точек для создания полигона</p>
          <p className="text-sm md:text-base mt-2">• Кликните на карте, чтобы добавить вершины</p>
          <p className="text-sm md:text-base">• Двойной клик или нажмите Enter для завершения</p>
          <p className="text-sm md:text-base">• Перетащите точки для изменения формы</p>
        </div>
      )}
    </div>
  );
}

export default FieldForm;