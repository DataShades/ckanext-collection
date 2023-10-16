const { resolve } = require("path");
const { src, dest, watch } = require("gulp");
const if_ = require("gulp-if");
const sourcemaps = require("gulp-sourcemaps");
const postcss = require("gulp-postcss");
const sass = require("gulp-sass")(require("sass"));
const touch = require("gulp-touch-cmd");

const isDev = () => !!process.env.DEBUG;

const assetsDir = resolve(__dirname, "ckanext/collection/assets");
const srcDir = resolve(assetsDir, "scss");
const destDir = resolve(assetsDir, "css");

const build = () =>
  src(resolve(srcDir, "collection.scss"))
    .pipe(if_(isDev, sourcemaps.init()))
    .pipe(sass({ outputStyle: "compressed" }).on('error', sass.logError))
    .pipe(postcss([require("postcss-combine-media-query")]))
    .pipe(if_(isDev, sourcemaps.write()))
    .pipe(dest(destDir))
    .pipe(touch());

const watchStyles = () =>
  watch(resolve(srcDir, "*.scss"), { ignoreInitial: false }, build);

exports.watch = watchStyles;
exports.build = build;
