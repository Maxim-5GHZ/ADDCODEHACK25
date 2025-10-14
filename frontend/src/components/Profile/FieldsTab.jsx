import React, { useState } from 'react';
import AddFieldOverlay from './AddFieldOverlay';

function FieldsTab() {
  const [showAddFieldOverlay, setShowAddFieldOverlay] = useState(false);
  const fields = [
    {id: 1, name: "first-field"},
    {id: 2, name: "second-field"},
    {id: 3, name: "third-field"},
    {id: 4, name: "fourth-field"}
  ];

  const handleAddFieldSubmit = (fieldData) => {
    console.log("Данные нового поля:", fieldData);
    setShowAddFieldOverlay(false);
  };

  return (
    <>
      <div className="container">
        <div className="text-3xl font-semibold mb-4">
          {fields.length === 0 ? "У вас ещё нет полей" : "Ваши поля:"}
        </div>
        <ul className="space-y-4 max-h-[20vh] overflow-y-auto">
          {fields.map(field => (
            <li key={field.id} className="bg-[#f6f6f6] rounded-xl px-6 py-4 flex justify-between items-center">
              <span className="text-xl font-medium text-gray-900">{field.name}</span>
              <button className="text-[#009e4f] font-bold hover:underline text-lg">
                Подробнее
              </button>
            </li>
          ))}
        </ul>
        <div>
          <button 
            onClick={() => setShowAddFieldOverlay(true)}
            className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] mt-6
            transition-[background-color] duration-100 cursor-pointer rounded-full text-3xl px-5 py-4 text-[var(--neutral-color)]"
          >
            Добавить поле
          </button>
        </div>
      </div>

      <AddFieldOverlay
        isVisible={showAddFieldOverlay}
        onClose={() => setShowAddFieldOverlay(false)}
        onSubmit={handleAddFieldSubmit}
      />
    </>
  );
}

export default FieldsTab;
