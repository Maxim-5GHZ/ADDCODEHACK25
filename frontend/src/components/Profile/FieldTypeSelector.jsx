import React from 'react';

function FieldTypeSelector({ fieldType, setFieldType, onFieldTypeChange }) {
  const handleTypeChange = (type) => {
    setFieldType(type);
    if (onFieldTypeChange) {
      onFieldTypeChange(type);
    }
  };

  return (
    <div className="mb-6">
      <label className="block text-2xl font-semibold mb-4 text-[var(--neutral-dark-color)]">Тип поля</label>
      <div className="flex gap-4">
        <button
          type="button"
          className={`px-6 py-4 rounded-full text-xl transition-all cursor-pointer shadow-2xs ${
            fieldType === 'polygon'
              ? 'bg-[var(--accent-color)] text-white hover:bg-[var(--accent-light-color)]'
              : 'bg-[var(--neutral-color)] text-gray-700 hover:bg-gray-200'
          }`}
          onClick={() => handleTypeChange('polygon')}
        >
          Полигон (3-5 вершин)
        </button>
        <button
          type="button"
          className={`px-6 py-4 rounded-full text-xl transition-all cursor-pointer shadow-2xs ${
            fieldType === 'point'
              ? 'bg-[var(--accent-color)] text-white hover:bg-[var(--accent-light-color)]'
              : 'bg-[var(--neutral-color)] text-gray-700 hover:bg-gray-200'
          }`}
          onClick={() => handleTypeChange('point')}
        >
          Точка с радиусом
        </button>
      </div>
    </div>
  );
}

export default FieldTypeSelector;