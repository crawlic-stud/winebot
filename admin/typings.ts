/* eslint-disable */
import {
  CollectionCustomizer,
  TAggregation,
  TConditionTree,
  TPaginatedFilter,
  TPartialRow,
  TSortClause
} from '@forestadmin/agent';

export type AdminsCustomizer = CollectionCustomizer<Schema, 'admins'>;
export type AdminsRecord = TPartialRow<Schema, 'admins'>;
export type AdminsConditionTree = TConditionTree<Schema, 'admins'>;
export type AdminsFilter = TPaginatedFilter<Schema, 'admins'>;
export type AdminsSortClause = TSortClause<Schema, 'admins'>;
export type AdminsAggregation = TAggregation<Schema, 'admins'>;

export type EventsCustomizer = CollectionCustomizer<Schema, 'events'>;
export type EventsRecord = TPartialRow<Schema, 'events'>;
export type EventsConditionTree = TConditionTree<Schema, 'events'>;
export type EventsFilter = TPaginatedFilter<Schema, 'events'>;
export type EventsSortClause = TSortClause<Schema, 'events'>;
export type EventsAggregation = TAggregation<Schema, 'events'>;

export type ProductsCustomizer = CollectionCustomizer<Schema, 'products'>;
export type ProductsRecord = TPartialRow<Schema, 'products'>;
export type ProductsConditionTree = TConditionTree<Schema, 'products'>;
export type ProductsFilter = TPaginatedFilter<Schema, 'products'>;
export type ProductsSortClause = TSortClause<Schema, 'products'>;
export type ProductsAggregation = TAggregation<Schema, 'products'>;


export type Schema = {
  'admins': {
    plain: {
      '_id': string;
      'user_id': number;
    };
    nested: {};
    flat: {};
  };
  'events': {
    plain: {
      '_id': string;
      'date': string;
      'description': string;
      'image_id': string;
      'name': string;
    };
    nested: {};
    flat: {};
  };
  'products': {
    plain: {
      '_id': string;
      'description': string;
      'image_id': string;
      'name': string;
      'price': number;
    };
    nested: {};
    flat: {};
  };
};
