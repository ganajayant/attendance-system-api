import React from 'react';
import { BrowserRouter, Route, Routes } from "react-router-dom";

import CaptureForm from './components/Camera/CaptureForm';
import Data from './components/Dashboard/Data';
import NavBar from './components/Navbar/Navbar';
import NotFound from './components/NotFound';

function App() {
  return <BrowserRouter>
    <NavBar></NavBar>
    <Routes>
      <Route exact path="/" element={<CaptureForm />} />
      <Route exact path="/dashboard" element={<Data />} />
      <Route exact path="*" element={<NotFound />} />
    </Routes>
  </BrowserRouter>;
}

export default App;
