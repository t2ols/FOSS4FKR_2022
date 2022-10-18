/**
 * @module ol/source/VectorTile
 */
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
import TileState from '../TileState.js';
import VectorRenderTile from '../VectorRenderTile.js';
import Tile from '../VectorTile.js';
import { toSize } from '../size.js';
import UrlTile from './UrlTile.js';
import { getKeyZXY, getKey } from '../tilecoord.js';
import { createXYZ, extentFromProjection, createForProjection } from '../tilegrid.js';
import { buffer as bufferExtent, getIntersection, intersects } from '../extent.js';
import EventType from '../events/EventType.js';
import { loadFeaturesXhr } from '../featureloader.js';
import { equals, remove } from '../array.js';
import { listen, unlistenByKey } from '../events.js';
/**
 * @typedef {Object} Options
 * @property {import("./Source.js").AttributionLike} [attributions] Attributions.
 * @property {boolean} [attributionsCollapsible=true] Attributions are collapsible.
 * @property {number} [cacheSize=128] Cache size.
 * @property {import("../extent.js").Extent} [extent]
 * @property {import("../format/Feature.js").default} [format] Feature format for tiles. Used and required by the default.
 * @property {boolean} [overlaps=true] This source may have overlapping geometries. Setting this
 * to `false` (e.g. for sources with polygons that represent administrative
 * boundaries or TopoJSON sources) allows the renderer to optimise fill and
 * stroke operations.
 * @property {import("../proj.js").ProjectionLike} [projection='EPSG:3857'] Projection of the tile grid.
 * @property {import("./State.js").default} [state] Source state.
 * @property {typeof import("../VectorTile.js").default} [tileClass] Class used to instantiate image tiles.
 * Default is {@link module:ol/VectorTile}.
 * @property {number} [maxZoom=22] Optional max zoom level.
 * @property {number} [minZoom] Optional min zoom level.
 * @property {number|import("../size.js").Size} [tileSize=512] Optional tile size.
 * @property {import("../tilegrid/TileGrid.js").default} [tileGrid] Tile grid.
 * @property {import("../Tile.js").LoadFunction} [tileLoadFunction]
 * Optional function to load a tile given a URL. Could look like this for pbf tiles:
 * ```js
 * function(tile, url) {
 *   tile.setLoader(function(extent, resolution, projection) {
 *     fetch(url).then(function(response) {
 *       response.arrayBuffer().then(function(data) {
 *         const format = tile.getFormat() // ol/format/MVT configured as source format
 *         const features = format.readFeatures(data, {
 *           extent: extent,
 *           featureProjection: projection
 *         });
 *         tile.setFeatures(features);
 *       });
 *     });
 *   });
 * }
 * ```
 * @property {import("../Tile.js").UrlFunction} [tileUrlFunction] Optional function to get tile URL given a tile coordinate and the projection.
 * @property {string} [url] URL template. Must include `{x}`, `{y}` or `{-y}`, and `{z}` placeholders.
 * A `{?-?}` template pattern, for example `subdomain{a-f}.domain.com`, may be
 * used instead of defining each one separately in the `urls` option.
 * @property {number} [transition] A duration for tile opacity
 * transitions in milliseconds. A duration of 0 disables the opacity transition.
 * @property {Array<string>} [urls] An array of URL templates.
 * @property {boolean} [wrapX=true] Whether to wrap the world horizontally.
 * When set to `false`, only one world
 * will be rendered. When set to `true`, tiles will be wrapped horizontally to
 * render multiple worlds.
 * @property {number} [zDirection=1] Indicate which resolution should be used
 * by a renderer if the view resolution does not match any resolution of the tile source.
 * If 0, the nearest resolution will be used. If 1, the nearest lower resolution
 * will be used. If -1, the nearest higher resolution will be used.
 */
/**
 * @classdesc
 * Class for layer sources providing vector data divided into a tile grid, to be
 * used with {@link module:ol/layer/VectorTile~VectorTile}. Although this source receives tiles
 * with vector features from the server, it is not meant for feature editing.
 * Features are optimized for rendering, their geometries are clipped at or near
 * tile boundaries and simplified for a view resolution. See
 * {@link module:ol/source/Vector} for vector sources that are suitable for feature
 * editing.
 *
 * @fires import("./Tile.js").TileSourceEvent
 * @api
 */
var VectorTile = /** @class */ (function (_super) {
    __extends(VectorTile, _super);
    /**
     * @param {!Options} options Vector tile options.
     */
    function VectorTile(options) {
        var _this = this;
        var projection = options.projection || 'EPSG:3857';
        var extent = options.extent || extentFromProjection(projection);
        var tileGrid = options.tileGrid || createXYZ({
            extent: extent,
            maxZoom: options.maxZoom !== undefined ? options.maxZoom : 22,
            minZoom: options.minZoom,
            tileSize: options.tileSize || 512
        });
        _this = _super.call(this, {
            attributions: options.attributions,
            attributionsCollapsible: options.attributionsCollapsible,
            cacheSize: options.cacheSize,
            opaque: false,
            projection: projection,
            state: options.state,
            tileGrid: tileGrid,
            tileLoadFunction: options.tileLoadFunction ? options.tileLoadFunction : defaultLoadFunction,
            tileUrlFunction: options.tileUrlFunction,
            url: options.url,
            urls: options.urls,
            wrapX: options.wrapX === undefined ? true : options.wrapX,
            transition: options.transition,
            zDirection: options.zDirection === undefined ? 1 : options.zDirection
        }) || this;
        /**
         * @private
         * @type {import("../format/Feature.js").default}
         */
        _this.format_ = options.format ? options.format : null;
        /**
         * @type {Object<string, import("./VectorTile").default>}
         */
        _this.loadingTiles_ = {};
        /**
         * @private
         * @type {Object<string, import("../VectorTile.js").default>}
         */
        _this.sourceTileByCoordKey_ = {};
        /**
         * @private
         * @type {Object<string, Array<import("../VectorTile.js").default>>}
         */
        _this.sourceTilesByTileKey_ = {};
        /**
         * @private
         * @type {boolean}
         */
        _this.overlaps_ = options.overlaps == undefined ? true : options.overlaps;
        /**
         * @protected
         * @type {typeof import("../VectorTile.js").default}
         */
        _this.tileClass = options.tileClass ? options.tileClass : Tile;
        /**
         * @private
         * @type {Object<string, import("../tilegrid/TileGrid.js").default>}
         */
        _this.tileGrids_ = {};
        return _this;
    }
    /**
     * @return {boolean} The source can have overlapping geometries.
     */
    VectorTile.prototype.getOverlaps = function () {
        return this.overlaps_;
    };
    /**
     * clear {@link module:ol/TileCache~TileCache} and delete all source tiles
     * @api
     */
    VectorTile.prototype.clear = function () {
        this.tileCache.clear();
        this.sourceTileByCoordKey_ = {};
        this.sourceTilesByTileKey_ = {};
    };
    /**
     * @param {number} pixelRatio Pixel ratio.
     * @param {import("../proj/Projection").default} projection Projection.
     * @param {VectorRenderTile} tile Vector image tile.
     * @return {Array<import("../VectorTile").default>} Tile keys.
     */
    VectorTile.prototype.getSourceTiles = function (pixelRatio, projection, tile) {
        var urlTileCoord = tile.wrappedTileCoord;
        var tileGrid = this.getTileGridForProjection(projection);
        var extent = tileGrid.getTileCoordExtent(urlTileCoord);
        var z = urlTileCoord[0];
        var resolution = tileGrid.getResolution(z);
        // make extent 1 pixel smaller so we don't load tiles for < 0.5 pixel render space
        bufferExtent(extent, -resolution, extent);
        var sourceTileGrid = this.tileGrid;
        var sourceExtent = sourceTileGrid.getExtent();
        if (sourceExtent) {
            getIntersection(extent, sourceExtent, extent);
        }
        var sourceZ = sourceTileGrid.getZForResolution(resolution, 1);
        var minZoom = sourceTileGrid.getMinZoom();
        var previousSourceTiles = this.sourceTilesByTileKey_[tile.getKey()];
        var sourceTiles, covered, loadedZ;
        if (previousSourceTiles && previousSourceTiles.length > 0 && previousSourceTiles[0].tileCoord[0] === sourceZ) {
            sourceTiles = previousSourceTiles;
            covered = true;
            loadedZ = sourceZ;
        }
        else {
            sourceTiles = [];
            loadedZ = sourceZ + 1;
            do {
                --loadedZ;
                covered = true;
                sourceTileGrid.forEachTileCoord(extent, loadedZ, function (sourceTileCoord) {
                    var coordKey = getKey(sourceTileCoord);
                    var sourceTile;
                    if (coordKey in this.sourceTileByCoordKey_) {
                        sourceTile = this.sourceTileByCoordKey_[coordKey];
                        var state = sourceTile.getState();
                        if (state === TileState.LOADED || state === TileState.ERROR || state === TileState.EMPTY) {
                            sourceTiles.push(sourceTile);
                            return;
                        }
                    }
                    else if (loadedZ === sourceZ) {
                        var tileUrl = this.tileUrlFunction(sourceTileCoord, pixelRatio, projection);
                        if (tileUrl !== undefined) {
                            sourceTile = new this.tileClass(sourceTileCoord, TileState.IDLE, tileUrl, this.format_, this.tileLoadFunction);
                            sourceTile.extent = sourceTileGrid.getTileCoordExtent(sourceTileCoord);
                            sourceTile.projection = projection;
                            sourceTile.resolution = sourceTileGrid.getResolution(sourceTileCoord[0]);
                            this.sourceTileByCoordKey_[coordKey] = sourceTile;
                            sourceTile.addEventListener(EventType.CHANGE, this.handleTileChange.bind(this));
                            sourceTile.load();
                        }
                    }
                    covered = false;
                    if (!sourceTile) {
                        return;
                    }
                    if (sourceTile.getState() !== TileState.EMPTY && tile.getState() === TileState.IDLE) {
                        tile.loadingSourceTiles++;
                        var key_1 = listen(sourceTile, EventType.CHANGE, function () {
                            var state = sourceTile.getState();
                            var sourceTileKey = sourceTile.getKey();
                            if (state === TileState.LOADED || state === TileState.ERROR) {
                                if (state === TileState.LOADED) {
                                    remove(tile.sourceTileListenerKeys, key_1);
                                    unlistenByKey(key_1);
                                    tile.loadingSourceTiles--;
                                    delete tile.errorSourceTileKeys[sourceTileKey];
                                }
                                else if (state === TileState.ERROR) {
                                    tile.errorSourceTileKeys[sourceTileKey] = true;
                                }
                                var errorTileCount = Object.keys(tile.errorSourceTileKeys).length;
                                if (tile.loadingSourceTiles - errorTileCount === 0) {
                                    tile.hifi = errorTileCount === 0;
                                    tile.sourceZ = sourceZ;
                                    tile.setState(TileState.LOADED);
                                }
                            }
                        });
                        tile.sourceTileListenerKeys.push(key_1);
                    }
                }.bind(this));
                if (!covered) {
                    sourceTiles.length = 0;
                }
            } while (!covered && loadedZ > minZoom);
        }
        if (tile.getState() === TileState.IDLE) {
            tile.setState(TileState.LOADING);
        }
        if (covered) {
            tile.hifi = sourceZ === loadedZ;
            tile.sourceZ = loadedZ;
            if (tile.getState() < TileState.LOADED) {
                tile.setState(TileState.LOADED);
            }
            else if (!previousSourceTiles || !equals(sourceTiles, previousSourceTiles)) {
                this.removeSourceTiles(tile);
                this.addSourceTiles(tile, sourceTiles);
            }
        }
        return sourceTiles;
    };
    /**
     * @param {VectorRenderTile} tile Tile.
     * @param {Array<import("../VectorTile").default>} sourceTiles Source tiles.
     */
    VectorTile.prototype.addSourceTiles = function (tile, sourceTiles) {
        this.sourceTilesByTileKey_[tile.getKey()] = sourceTiles;
        for (var i = 0, ii = sourceTiles.length; i < ii; ++i) {
            sourceTiles[i].consumers++;
        }
    };
    /**
     * @param {VectorRenderTile} tile Tile.
     */
    VectorTile.prototype.removeSourceTiles = function (tile) {
        var tileKey = tile.getKey();
        if (tileKey in this.sourceTilesByTileKey_) {
            var sourceTiles = this.sourceTilesByTileKey_[tileKey];
            for (var i = 0, ii = sourceTiles.length; i < ii; ++i) {
                var sourceTile = sourceTiles[i];
                sourceTile.consumers--;
                if (sourceTile.consumers === 0) {
                    sourceTile.dispose();
                    delete this.sourceTileByCoordKey_[getKey(sourceTile.tileCoord)];
                }
            }
        }
        delete this.sourceTilesByTileKey_[tileKey];
    };
    /**
     * @inheritDoc
     */
    VectorTile.prototype.getTile = function (z, x, y, pixelRatio, projection) {
        var coordKey = getKeyZXY(z, x, y);
        var key = this.getKey();
        var tile;
        if (this.tileCache.containsKey(coordKey)) {
            tile = /** @type {!import("../Tile.js").default} */ (this.tileCache.get(coordKey));
            if (tile.key === key) {
                return tile;
            }
        }
        var tileCoord = [z, x, y];
        var urlTileCoord = this.getTileCoordForTileUrlFunction(tileCoord, projection);
        var sourceExtent = this.getTileGrid().getExtent();
        var tileGrid = this.getTileGridForProjection(projection);
        if (urlTileCoord && sourceExtent) {
            var tileExtent = tileGrid.getTileCoordExtent(urlTileCoord);
            // make extent 1 pixel smaller so we don't load tiles for < 0.5 pixel render space
            bufferExtent(tileExtent, -tileGrid.getResolution(z), tileExtent);
            if (!intersects(sourceExtent, tileExtent)) {
                urlTileCoord = null;
            }
        }
        var empty = true;
        if (urlTileCoord !== null) {
            var sourceTileGrid = this.tileGrid;
            var resolution = tileGrid.getResolution(z);
            var sourceZ = sourceTileGrid.getZForResolution(resolution, 1);
            // make extent 1 pixel smaller so we don't load tiles for < 0.5 pixel render space
            var extent = tileGrid.getTileCoordExtent(urlTileCoord);
            bufferExtent(extent, -resolution, extent);
            sourceTileGrid.forEachTileCoord(extent, sourceZ, function (sourceTileCoord) {
                empty = empty && !this.tileUrlFunction(sourceTileCoord, pixelRatio, projection);
            }.bind(this));
        }
        var newTile = new VectorRenderTile(tileCoord, empty ? TileState.EMPTY : TileState.IDLE, urlTileCoord, this.tileGrid, this.getSourceTiles.bind(this, pixelRatio, projection), this.removeSourceTiles.bind(this));
        newTile.key = key;
        if (tile) {
            newTile.interimTile = tile;
            newTile.refreshInterimChain();
            this.tileCache.replace(coordKey, newTile);
        }
        else {
            this.tileCache.set(coordKey, newTile);
        }
        return newTile;
    };
    /**
     * @inheritDoc
     */
    VectorTile.prototype.getTileGridForProjection = function (projection) {
        var code = projection.getCode();
        var tileGrid = this.tileGrids_[code];
        if (!tileGrid) {
            // A tile grid that matches the tile size of the source tile grid is more
            // likely to have 1:1 relationships between source tiles and rendered tiles.
            var sourceTileGrid = this.tileGrid;
            tileGrid = createForProjection(projection, undefined, sourceTileGrid ? sourceTileGrid.getTileSize(sourceTileGrid.getMinZoom()) : undefined);
            this.tileGrids_[code] = tileGrid;
        }
        return tileGrid;
    };
    /**
     * @inheritDoc
     */
    VectorTile.prototype.getTilePixelRatio = function (pixelRatio) {
        return pixelRatio;
    };
    /**
     * @inheritDoc
     */
    VectorTile.prototype.getTilePixelSize = function (z, pixelRatio, projection) {
        var tileGrid = this.getTileGridForProjection(projection);
        var tileSize = toSize(tileGrid.getTileSize(z), this.tmpSize);
        return [Math.round(tileSize[0] * pixelRatio), Math.round(tileSize[1] * pixelRatio)];
    };
    return VectorTile;
}(UrlTile));
export default VectorTile;
/**
 * Sets the loader for a tile.
 * @param {import("../VectorTile.js").default} tile Vector tile.
 * @param {string} url URL.
 */
export function defaultLoadFunction(tile, url) {
    var loader = loadFeaturesXhr(url, tile.getFormat(), tile.onLoad.bind(tile), tile.onError.bind(tile));
    tile.setLoader(loader);
}
//# sourceMappingURL=VectorTile.js.map