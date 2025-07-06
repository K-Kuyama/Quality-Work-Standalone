import React, { useState, useEffect } from 'react';
import SettingsEditor from "./SettingsEditor";
import DBLoader from "./DBLoader";
//import FileLoader from "./FileLoader";
import DBSettings from "./DBSettings"

function SettingsSpace(props){

    if (props.category == "audio"){
        return (
            <SettingsEditor category={props.category}/>
        )
    }
    if (props.category == "db_settings"){
        return (
            <DBSettings />
        )
    }
    /*
    if (props.category == "db_migration"){
        return (
            <DBLoader />
        )
    }
    if (props.category == "db_file_import"){
        return (
            <FileLoader />
        )  
    }
    if (props.category == "initial_settings"){

    }
    */

}

export default SettingsSpace;