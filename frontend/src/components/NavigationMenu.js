//import React, { useState, useEffect } from 'react';
import Cookies from "universal-cookie";
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
//import Button from 'react-bootstrap/Button';
import 'bootstrap/dist/css/bootstrap.min.css';

//import ActivityListPage from "../pages/ActivityListPage";
//import AllGraphsPage from "../pages/AllGraphsPage";
import Settings from "../Settings";

//onst cookies = new Cookies();

function NavigationMenu(props){


    if (Settings.FULL_FUNCTIONS) {        
        return(
            <Navbar expand="lg" className="bg-body-tertiary"  data-bs-theme="dark">
                    <Container>
                        <Navbar.Brand href="#home">QW</Navbar.Brand>
                        {/* <div className="username"> {username} </div> */}
                        <Navbar.Toggle aria-controls="basic-navbar-nav" />
                        <Navbar.Collapse id="basic-navbar-nav">
                            <Nav className="mr-auto">            	
                                <Nav.Link href={Settings.HOME_PATH+"/dashboard"}>ダッシュボード</Nav.Link>
                                <Nav.Link href={Settings.HOME_PATH+"/"}>アクティビティリスト</Nav.Link>                                
                                <NavDropdown title="データグラフ" id="basic-nav-dropdown">
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/date_graphs"}> 日次集計情報 </NavDropdown.Item>
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/week_graphs"}> 週次集計情報 </NavDropdown.Item>
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/month_graphs"}> 月次集計情報 </NavDropdown.Item>
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/year_graphs"}> 年次集計情報 </NavDropdown.Item>
                                    <NavDropdown.Divider />
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/all_graphs"}> 総合時間情報 </NavDropdown.Item>
                                </NavDropdown>
                                <NavDropdown title="カテゴリーグラフ" id="category-nav-dropdown">
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/categorize"}> 円グラフ </NavDropdown.Item>
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/multi_categorize"}> 複合円グラフ </NavDropdown.Item>  
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/bar_graphs"}> 時間バーグラフ</NavDropdown.Item>                              
                                </NavDropdown>
                                <Nav.Link href={Settings.HOME_PATH+"/editor"}>カテゴリーエディター</Nav.Link>   
                            </Nav>
                        </Navbar.Collapse>
                    </Container>
                    
            </Navbar>	
        );
    } else {
        return(
            <Navbar expand="lg" className="bg-body-tertiary"  data-bs-theme="dark">
                    <Container>
                        <Navbar.Brand href="#home">QT</Navbar.Brand>
                        {/* <div className="username"> {username} </div> */}
                        <Navbar.Toggle aria-controls="basic-navbar-nav" />
                        <Navbar.Collapse id="basic-navbar-nav">
                            <Nav className="mr-auto">            	
                                <Nav.Link href={Settings.HOME_PATH+"/dashboard"}>ダッシュボード</Nav.Link>
                                <Nav.Link href={Settings.HOME_PATH+"/"}>アクティビティリスト</Nav.Link>   
                                <Nav.Link href={Settings.HOME_PATH+"/all_graphs"}>グラフ</Nav.Link>                       
                            </Nav>
                        </Navbar.Collapse>
                    </Container>
                    
               </Navbar>	
        );
    }


}

export default NavigationMenu;