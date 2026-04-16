import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileSearch, 
  ShieldCheck, 
  UserCheck, 
  ClipboardCheck, 
  LogOut, 
  LogIn, 
  ShieldAlert,
  Sun,
  Moon
} from 'lucide-react';

const Layout = ({ 
  children, 
  activeSection, 
  setActiveSection, 
  user, 
  onLoginClick,
  isDark,
  toggleTheme
}) => {
  const navItems = [
    { id: 'extract', label: 'Extract', icon: FileSearch },
    { id: 'tamper', label: 'Tamper Check', icon: ShieldAlert },
    { id: 'face', label: 'Face Match', icon: UserCheck },
    { id: 'verify', label: 'Verify', icon: ClipboardCheck },
  ];

  return (
    <div className="flex min-h-screen font-inter">
      {/* Sidebar */}
      <aside className="w-72 glass-card-dark rounded-none border-y-0 border-l-0 border-r border-white/10 flex flex-col fixed h-full z-20 overflow-hidden">
        {/* Animated Background Glow in Sidebar */}
        <motion.div 
          animate={{ opacity: isDark ? 0.3 : 0.1 }}
          className="absolute -top-20 -left-20 w-64 h-64 bg-gov-saffron rounded-full blur-[80px] pointer-events-none" 
        />

        <div className="p-8 pb-4 relative z-10">
          <div className="flex items-center gap-3 mb-1">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-lg ${isDark ? 'bg-gov-saffron/20 border border-gov-saffron/30' : 'bg-gov-saffron shadow-gov-saffron/30'}`}>
              <ShieldCheck className={isDark ? 'text-gov-saffron' : 'text-gov-green'} size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white">DocVerify</h1>
              <p className="text-[10px] uppercase tracking-[0.2em] text-gov-saffron font-bold">Government Portal</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-4 py-8 space-y-2 relative z-10">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id)}
              className={`nav-item w-full ${activeSection === item.id ? 'active' : ''}`}
            >
              <item.icon size={20} strokeWidth={activeSection === item.id ? 2.5 : 2} />
              <span className={`font-medium ${activeSection === item.id ? 'text-white' : 'text-white/60'}`}>
                {item.label}
              </span>
              {activeSection === item.id && (
                <motion.div 
                  layoutId="activeNav"
                  className="ml-auto w-1.5 h-1.5 rounded-full bg-gov-saffron"
                />
              )}
            </button>
          ))}
        </nav>

        <div className="p-6 border-t border-white/5 space-y-2 relative z-10">
          <button 
            onClick={toggleTheme}
            className="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition-all hover:bg-white/5 text-white/50 hover:text-white group"
          >
            <AnimatePresence mode="wait" initial={false}>
              <motion.div
                key={isDark ? 'dark' : 'light'}
                initial={{ rotate: -90, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: 90, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                {isDark ? <Sun size={18} /> : <Moon size={18} />}
              </motion.div>
            </AnimatePresence>
            <span className="text-sm font-medium">{isDark ? 'Light' : 'Dark'} Mode</span>
          </button>
          
          <button 
            onClick={onLoginClick}
            className="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition-all hover:bg-white/5 text-white/50 hover:text-white"
          >
            {user ? <LogOut size={18} /> : <LogIn size={18} />}
            <span className="text-sm font-medium">{user ? 'Log Out' : 'Sign In'}</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-72 relative transition-colors duration-300">
        <header className="h-20 flex items-center justify-between px-10 sticky top-0 z-10">
          <div>
            <AnimatePresence mode="wait">
              <motion.h2 
                key={activeSection}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                className={`text-2xl font-bold capitalize transition-colors ${isDark ? 'text-white' : 'text-gov-green'}`}
              >
                {activeSection.replace('-', ' ')}
              </motion.h2>
            </AnimatePresence>
          </div>
          
          {user && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-3 glass-card px-4 py-2 border-0 shadow-sm"
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs text-white font-bold ${isDark ? 'bg-gov-saffron text-gov-green' : 'bg-gov-green'}`}>
                {user.username[0].toUpperCase()}
              </div>
              <span className={`text-sm font-medium ${isDark ? 'text-white/90' : 'text-gov-green'}`}>{user.full_name || user.username}</span>
            </motion.div>
          )}
        </header>

        <div className="p-10 pb-20 max-w-6xl mx-auto">
          {children}
        </div>
        
        {/* Decorative elements */}
        <div className={`fixed bottom-10 right-10 pointer-events-none transition-opacity duration-1000 ${isDark ? 'opacity-[0.03]' : 'opacity-[0.06]'}`}>
          <ShieldCheck size={300} strokeWidth={0.5} className={isDark ? 'text-white' : 'text-gov-green'} />
        </div>
      </main>
    </div>
  );
};

export default Layout;
