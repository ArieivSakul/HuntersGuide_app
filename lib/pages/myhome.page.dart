// ignore_for_file: prefer_const_constructors, unnecessary_new, deprecated_member_use, avoid_unnecessary_containers, sized_box_for_whitespace, dead_code

import 'package:flutter/material.dart';

class MyHomePage extends StatefulWidget {
  const MyHomePage({Key? key}) : super(key: key);

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String dropdownvalue = 'Menu:';

  // Lista de itens do menu
  var items = ['Menu:', 'Monstros Grandes', 'Monstros Pequenos', 'Sobre'];

  get body => null;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Color.fromARGB(255, 6, 109, 28),
        title: Center(
          child: SizedBox(
            width: 100,
            child: Image.asset("assets/app_logo.png"),
          ),
        ),
        leading: Container(
          height: 40,
          width: 40,
          decoration: new BoxDecoration(
            image: new DecorationImage(
              image: AssetImage("assets/user-picture.png"),
              fit: BoxFit.fitHeight,
            ),
          ),
        ),
        actions: <Widget>[
          Container(
            width: 60,
            child: FlatButton(
              child: Icon(
                Icons.search,
                color: Color(0xFFBABABA),
              ),
              onPressed: () => {},
            ),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            DropdownButton(
              // valor inicial
              value: dropdownvalue,

              // icone de menu arrastavel
              icon: const Icon(Icons.keyboard_arrow_down),

              // Array list
              items: items.map((String items) {
                return DropdownMenuItem(
                  value: items,
                  child: Text(items),
                );
              }).toList(),
              onChanged: (String? newValue) {
                setState(() {
                  dropdownvalue = newValue!;
                });
              },
            ),
          ],
        ),
      ),
    );
  }
}
