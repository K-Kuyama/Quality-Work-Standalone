import React, { useState } from 'react';
import SettingsPanel from "../components/SettingsPanel"
//import SettingsEditor from "../components/SettingsEditor"
import SettingsSpace from '../components/SettingsSpace';

function SettingsPage(){

    const [category, setCategory] = useState('audio')

    return(
		<div className="app_page">
			<div className="sidebar">
				<div id="controls" className="controls">
					<SettingsPanel handler={setCategory} />
				</div>
			</div>
			<div className="contents">
				<SettingsSpace category={category} />
			</div>
		</div>
	)
}

export default SettingsPage;