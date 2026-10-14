#!/usr/bin/env node
import {createRequire} from "node:module";
import {fileURLToPath} from "node:url";
const require=createRequire(new URL("../../../web/package.json",import.meta.url));
const express=require("express"),app=express();
app.get("/favicon.ico",(_req,res)=>res.sendStatus(204));
const studio=process.argv.includes("--studio");
app.use(express.static(fileURLToPath(new URL(studio?"./studio/out/":"./out/",import.meta.url))));
const port=process.argv.slice(2).find(value=>/^\d+$/.test(value))||0;
const server=app.listen(Number(port),"127.0.0.1",()=>console.log(`One Less Errand: http://127.0.0.1:${server.address().port}/`));
