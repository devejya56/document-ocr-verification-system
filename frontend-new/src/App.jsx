import React, { useState } from 'react';
import VantageLayout from './components/VantageLayout';
import ExtractSection from './components/sections/ExtractSection';
import TamperSection from './components/sections/TamperSection';
import FaceMatchSection from './components/sections/FaceMatchSection';
import VerifySection from './components/sections/VerifySection';

function App() {
  const [activeSection, setActiveSection] = useState('extract');
  const [user, setUser] = useState({ username: 'Admin' });

  const renderSection = () => {
    switch (activeSection) {
      case 'extract':
        return <ExtractSection />;
      case 'tamper':
        return <TamperSection />;
      case 'face':
        return <FaceMatchSection />;
      case 'verify':
        return <VerifySection />;
      default:
        return <ExtractSection />;
    }
  };

  return (
    <VantageLayout 
      activeSection={activeSection} 
      setActiveSection={setActiveSection}
      user={user}
    >
      <div className="w-full">
         {renderSection()}
      </div>
    </VantageLayout>
  );
}

export default App;
