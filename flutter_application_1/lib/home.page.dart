// ignore_for_file: prefer_const_constructors, unnecessary_new, deprecated_member_use, avoid_unnecessary_containers

import 'package:flutter/material.dart';

class HomePage extends StatelessWidget {
  const HomePage({ Key? key }) : super(key: key);

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
          // ignore: sized_box_for_whitespace
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
      body: Container(
        color: Color(0xFFF2F3F6),
        child: ListView(
          children: <Widget>[
              cardItem(),
              cardItem(),
              cardItem(),
              cardItem(),
              cardItem(),
              cardItem(),
          ],
        ),
      ),
    );
  }
}

Widget cardItem(){
  return Card(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      // ignore: prefer_const_literals_to_create_immutables
      children: <Widget>[
        const ListTile(
          leading: CircleAvatar(
            backgroundImage: AssetImage(
              "user-picture.png"),
          ),
          title: Text("Caçador"),
          subtitle: Text("03/05/2022 19:56"),
          trailing: Icon(Icons.more_vert),
        ),
        Container(
          child: Image.asset("assets/monster wallpaper 29.jpg"),
        ),
        Container(
          padding: EdgeInsets.all(10),
          child: Text(
            "Hunters faces the fierce Glavenus on the Guided Lands",
          ),
        ),
     ],
    ),
  );
}