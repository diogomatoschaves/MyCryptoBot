import { createRoot } from 'react-dom/client';
import {BrowserRouter as Router, Route} from 'react-router-dom';
import './index.css';
import AppLogin from "./components/AppLogin";

createRoot(document.getElementById('root')!).render(
  <Router>
    <Route render={({location, history}) => (
      <AppLogin location={location} history={history}/>
    )}>
    </Route>
  </Router>
);
