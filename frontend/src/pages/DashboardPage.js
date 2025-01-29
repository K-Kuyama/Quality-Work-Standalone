import SimpleDashboardPage from "./SimpleDashboardPage.js";
import FullDashboardPage from "./FullDashboardPage.js";
import Settings from "../Settings.js";

function DashboardPage(){

    if(Settings.FULL_FUNCTIONS){
        return(
            < FullDashboardPage />
        );
    } else {
        return(
            < SimpleDashboardPage />
        );
    }

}

export default DashboardPage;