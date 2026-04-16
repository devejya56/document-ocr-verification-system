import React from 'react';
import { motion } from 'framer-motion';

const InfographicBackground = ({ isDark }) => {
  return (
    <div className={`fixed inset-0 -z-10 overflow-hidden pointer-events-none transition-colors duration-700 ${isDark ? 'bg-[#0a0f0c]' : 'bg-[#f0f2f5]'}`}>
      <svg className="absolute w-full h-full opacity-20" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="dotGrid" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1.5" fill={isDark ? "white" : "#1B3022"} opacity={isDark ? "0.1" : "0.08"} />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#dotGrid)" />
      </svg>
      
      {/* Dynamic Data Nodes */}
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ 
            opacity: isDark ? [0.1, 0.2, 0.1] : [0.2, 0.4, 0.2],
            scale: [1, 1.2, 1],
            x: [0, Math.random() * 40 - 20, 0],
            y: [0, Math.random() * 40 - 20, 0]
          }}
          transition={{
            duration: 8 + Math.random() * 5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 2
          }}
          className={`absolute rounded-full blur-3xl ${isDark ? 'bg-gov-saffron' : 'bg-gov-green'}`}
          style={{
            width: `${15 + Math.random() * 20}rem`,
            height: `${15 + Math.random() * 20}rem`,
            left: `${Math.random() * 80}%`,
            top: `${Math.random() * 80}%`,
          }}
        />
      ))}

      {/* Connection Lines (Static SVG decor) */}
      <svg className={`absolute inset-0 w-full h-full transition-opacity duration-700 ${isDark ? 'opacity-10' : 'opacity-[0.03]'}`} style={{ stroke: isDark ? 'white' : '#1B3022', strokeWidth: 1 }}>
        <line x1="10%" y1="20%" x2="40%" y2="50%" />
        <line x1="40%" y1="50%" x2="30%" y2="80%" />
        <line x1="70%" y1="10%" x2="50%" y2="40%" />
        <line x1="50%" y1="40%" x2="90%" y2="60%" />
      </svg>
    </div>
  );
};

export default InfographicBackground;
