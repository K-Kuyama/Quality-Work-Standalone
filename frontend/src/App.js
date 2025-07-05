import {BrowserRouter, Routes, Route } from 'react-router-dom';
// import Container from 'react-bootstrap/Container';
import NavigationMenu from './components/NavigationMenu';
import ActivityListPage from './pages/ActivityListPage';
import InputOperationGraphsPage from './pages/InputOperationGraphsPage';
import BarGraphsPage from './pages/BarGraphsPage';
import AllGraphsPage from './pages/AllGraphsPage';
import CategorizedViewPage from './pages/CategorizedViewPage';
import MultiCategorizedViewPage from './pages/MultiCategorizedViewPage';
import UserDefPage from './pages/UserDefPage';
import AudioActivityPage from './pages/AudioActivityPage';
//import DataFilesPage from './pages/DataFilesPage';
//import DBMigrationPage from './pages/DBMigrationPage'
import DashboardPage from './pages/DashboardPage';
import SettingsPage from './pages/SettingsPage';
//import TestPage from './TestPage'
import {ShowPolicyContext, useShowPolicy} from "./Context"
import Settings from './Settings';

import React, {useState, createContext, useCallback} from 'react'

/*
export const ShowPolicyContext = createContext();


function useShowPolicy(){
	const [policy, setPolicy] = useState(0);
	const updatePolicy = useCallback((policy) => {setPolicy(policy)},[]);  
	//console.log(policy);
	//console.log(updatePolicy);
	return({policy, updatePolicy});
}
*/

function App(){
	const ctx = useShowPolicy();
	console.log(ctx)
	return (
		<div>
    		<BrowserRouter basename={Settings.HOME_PATH}>
			<ShowPolicyContext.Provider value ={ctx}>
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
				<Route path="/audios" element={<AudioActivityPage />} />
				<Route path="/settings" element={<SettingsPage />} />
        	</Routes>

			</ShowPolicyContext.Provider>
        	</BrowserRouter>
        </div>
      );        
 


}
export default App;
