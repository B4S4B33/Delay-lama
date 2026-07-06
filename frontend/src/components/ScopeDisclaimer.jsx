import React from 'react';

function ScopeDisclaimer() {
  return (
    <div className="scope-disclaimer">
      <span>ℹ️</span>
      <span>
        <strong>Scope:</strong> This model is trained on US domestic flights (2018-2022).
        Predictions apply only to US carriers and airports. Not valid for international flights.
      </span>
    </div>
  );
}

export default ScopeDisclaimer;
