import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-main-area',
  templateUrl: './main-area.component.html',
  styleUrls: ['./main-area.component.css']
})
export class MainAreaComponent implements OnInit {

  colors = [
    'red', 'pink', 'purple', 'indigo', 'blue', 'cyan', 'teal', 'green',
    'lime', 'yellow', 'amber', 'orange', 'brown', 'grey', 'white', 'black'
  ];

  constructor() { }

  ngOnInit() {
  }

}
