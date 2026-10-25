"use client";

import React from "react";

interface NavbarProps {
  statusText?: string;
}

export default function Navbar({ statusText = "Audio integrity analysis" }: NavbarProps) {
  return (
    <header className="topbar">
      <a className="brand" href="/" aria-label="VoxShield home">
        <span className="brand-mark" aria-hidden="true">V</span>
        <span>
          VoxShield<span className="brand-dot">.</span>
        </span>
      </a>
      <div className="topbar-right">
        <span className="topbar-note">
          <span className="status-dot" /> {statusText}
        </span>
      </div>
    </header>
  );
}
