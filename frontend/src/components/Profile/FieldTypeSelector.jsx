import React from 'react';

function FieldTypeSelector({ fieldType, setFieldType }) {
  return (
    <div className="mb-6">
      <label className="block text-2xl font-semibold mb-4">Тип поля</label>
      <div className="flex gap-4">
        <button
          type="button"
          className={`px-6 py-3 rounded-xl text-xl transition-all ${
            fieldType === 'polygon'
              ? 'bg-[var(--accent-color)] text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          onClick={() => setFieldType('polygon')}
        >
          Полигон (3-5 вершин)
        </button>
        <button
          type="button"
          className={`px-6 py-3 rounded-xl text-xl transition-all ${
            fieldType === 'point'
              ? 'bg-[var(--accent-color)] text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          onClick={() => setFieldType('point')}
        >
          Точка с радиусом
        </button>
      </div>
    </div>
  );
}

export default FieldTypeSelector;
