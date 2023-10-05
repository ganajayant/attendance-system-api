import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";


const Header = () => {
  return (
    <>
      <div className="header">
        <Link to={'/'}>
          <div className="logo">
            <span>A</span>ttendance <span>T</span>racking <span>S</span>ystem
          </div>
        </Link>
        <ul className="navbar">
          <li className="nav-item">
            <a href="/dashboard">Sheet</a>
          </li>
        </ul>
      </div>
    </>
  );
};

export default Header;
