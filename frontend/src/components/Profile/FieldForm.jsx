import React from 'react';

function FieldForm({ fieldType, fieldName, setFieldName, radius, setRadius, area, perimeter }) {
  return (
    <div className="space-y-6">
      <div>
        <label className="block text-2xl font-semibold mb-2" htmlFor="fieldName">
          Название поля
        </label>
        <input
          id="fieldName"
          type="text"
          value={fieldName}
          onChange={(e) => setFieldName(e.target.value)}
          className="w-full border rounded-xl px-6 py-4 text-xl focus:outline-none focus:ring-2 focus:ring-[#009e4f]"
          placeholder="Введите название поля"
        />
      </div>

      {area && (
        <div className="bg-green-50 p-4 rounded-xl border border-green-200">
          <p className="text-lg font-semibold text-green-800">
            Площадь: {area}
          </p>
          {perimeter && (
            <p className="text-lg font-semibold text-green-800 mt-2">
              Периметр: {perimeter}
            </p>
          )}
        </div>
      )}

      {fieldType === 'point' && (
        <div>
          <label className="block text-2xl font-semibold mb-2" htmlFor="radius">
            Радиус (метры)
          </label>
          <input
            id="radius"
            type="number"
            value={radius}
            onChange={(e) => setRadius(parseInt(e.target.value) || 100)}
            className="w-full border rounded-xl px-6 py-4 text-xl focus:outline-none focus:ring-2 focus:ring-[#009e4f]"
            placeholder="Введите радиус"
            min="1"
          />
        </div>
      )}

      {fieldType === 'polygon' && (
        <div className="text-lg text-gray-600 bg-yellow-50 p-4 rounded-xl">
          <p>ℹ️ Выберите на карте от 3 до 5 точек для создания полигона</p>
          <p className="text-sm mt-2">• Кликните на карте, чтобы добавить вершины</p>
          <p className="text-sm">• Двойной клик или нажмите Enter для завершения</p>
          <p className="text-sm">• Перетащите точки для изменения формы</p>
        </div>
      )}
    </div>
  );
}

export default FieldForm;
