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
/**
 * @module ol/layer/Tile
 */
import BaseTileLayer from './BaseTile.js';
import CanvasTileLayerRenderer from '../renderer/canvas/TileLayer.js';
/**
 * @classdesc
 * For layer sources that provide pre-rendered, tiled images in grids that are
 * organized by zoom levels for specific resolutions.
 * Note that any property set in the options is set as a {@link module:ol/Object~BaseObject}
 * property on the layer object; for example, setting `title: 'My Title'` in the
 * options means that `title` is observable, and has get/set accessors.
 *
 * @api
 */
var TileLayer = /** @class */ (function (_super) {
    __extends(TileLayer, _super);
    /**
     * @param {import("./BaseTile.js").Options=} opt_options Tile layer options.
     */
    function TileLayer(opt_options) {
        return _super.call(this, opt_options) || this;
    }
    /**
     * Create a renderer for this layer.
     * @return {import("../renderer/Layer.js").default} A layer renderer.
     * @protected
     */
    TileLayer.prototype.createRenderer = function () {
        return new CanvasTileLayerRenderer(this);
    };
    return TileLayer;
}(BaseTileLayer));
export default TileLayer;
//# sourceMappingURL=Tile.js.map