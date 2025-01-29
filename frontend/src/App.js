import React from 'react';
import {BrowserRouter, Routes, Route } from 'react-router-dom';
//import Container from 'react-bootstrap/Container';
import NavigationMenu from './components/NavigationMenu';
import ActivityListPage from './pages/ActivityListPage';
import InputOperationGraphsPage from './pages/InputOperationGraphsPage';
import BarGraphsPage from './pages/BarGraphsPage';
import AllGraphsPage from './pages/AllGraphsPage';
import CategorizedViewPage from './pages/CategorizedViewPage';
import UserDefPage from './pages/UserDefPage';
import MultiCategorizedViewPage from './pages/MultiCategorizedViewPage';
import DashboardPage from './pages/DashboardPage';
import Settings from './Settings';

function App(){

	return (
		<div>
    		<BrowserRouter basename={Settings.HOME_PATH}>
       		<NavigationMenu />
        	<Routes>
				<Route path="/dashboard" element={<DashboardPage />} />
        		<Route path="/" element={<ActivityListPage />} />
        		<Route path="/date_graphs" element={<InputOperationGraphsPage kind_of_period="day" />} />
        		<Route path="/week_graphs" element={<InputOperationGraphsPage kind_of_period="week" />} />
        		<Route path="/month_graphs" element={<InputOperationGraphsPage kind_of_period="month" />} />
        		<Route path="/year_graphs" element={<InputOperationGraphsPage kind_of_period="year" />} />
        		<Route path="/bar_graphs" element={<BarGraphsPage />} />
        		<Route path="/all_graphs" element={<AllGraphsPage />} />
        		<Route path="/categorize" element={<CategorizedViewPage />} />
        		<Route path="/multi_categorize" element={<MultiCategorizedViewPage />} />
				<Route path="/editor" element={<UserDefPage />} />

        	</Routes>
        	</BrowserRouter>
        </div>
      );        
 


}
export default App;
